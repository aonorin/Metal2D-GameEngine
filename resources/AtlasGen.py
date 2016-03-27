#!/usr/local/bin/python

'''
Needs to be updated to do something like casset/Dir/images outputs to outcasset/dirAtlas
instead of making all the images into one atlas
'''

from PIL import Image
import json
import os
import shutil
import sys

class FileManager:
  def __init__(self, inPath, outPath):
    if not os.getcwd().endswith('/resources'):
      ospath = os.getcwd() + '/resources/'
    else:
      ospath = os.getcwd() + '/'
    self.inPath = ospath + inPath
    self.outPath = ospath + outPath
    self.twoImages = []
    self.thrImages = []

  def updateRequired(self):
    with open(self.inPath + '/Contents.json') as contents:
      c = json.load(contents)

      try:
        c['info']['customVersion']
        return False
      except:
        return True

  def deleteOldData(self):
    try:
      shutil.rmtree(self.outPath)
    except:
      pass
    try:
      os.mkdir(self.outPath)
    except:
      pass
    shutil.copyfile(self.inPath + '/Contents.json', self.outPath + '/Contents.json')
      
  def getImageData(self):
    imageDirs = [i[0] for i in os.walk(self.inPath) if i[0].endswith('imageset')] 
    imageConts = [i + '/Contents.json' for i in imageDirs]

    for c in imageConts:
      f = open(c, 'r')
      cont = json.load(f)
      images = cont['images']

      for i in images:
        try:
          p = i['filename']
          d = c[:-len('Contents.json')]
          if i['scale'] == '2x':
            self.twoImages.append(d + p)
          else:
            self.thrImages.append(d + p)
        except:
          if i['scale'] != '1x':
            print(c + ' no file for ' + i['scale'])
          pass
    return (self.twoImages, self.thrImages)

  #only designing this to handle one extra depth I think for now anyway
  #I'm pretty sure that's as big as I organize anything 
  def filterByFolder(self, data):
    pathNum = len(self.inPath.split('/'))
    top = filter(lambda x: len(x.split('/')) == pathNum + 2, data)
    deeper = filter(lambda x: len(x.split('/')) == pathNum + 3, data)

    subfolders = {'Atlas': top}
    for directory in deeper:
      folder = self.getFolderName(directory)
      try:
        subfolders[folder].append(directory)
      except:
        subfolders[folder] = [directory]
    return subfolders
      
  def getFolderName(self, directory):
    folders = directory.split('/')
    for (i, f) in enumerate(folders):
      if f.endswith('imageset'):
        return folders[i - 1]
    return 'Atlas'

  def saveImageData(self, filename, imageData, scale):
    outdir = self.outPath + '/' + filename + '.imageset/'

    try:
      os.mkdir(outdir)
    except:
      pass

    imageData.save(outdir + filename + '@' + scale + '.png')
    
    try:
      f = open(outdir + 'Contents.json', 'r+')
    except:
      f = open(outdir + 'Contents.json', 'w+')

    try:
      contents = json.load(f)
      #hopefully this just works lololol
      if scale == '2x':
        contents['images'][1]['filename'] = filename + '@2x.png'
      else:
        contents['images'][2]['filename'] = filename + '@3x.png'
    except ValueError:
      contents = {
        'images': [
          {
            'idiom': 'universal',
            'scale': '1x'
          },
          {
            'idiom': 'universal',
            'scale': '2x'
          },
          {
            'idiom': 'universal',
            'scale': '3x'
          }
        ],
        'info': {
          'version': 1,
          'author': 'xcode'
        }
      }
      if scale == '2x':
        contents['images'][1]['filename'] = filename + '@2x.png'
      else:
        contents['images'][2]['filename'] = filename + '@3x.png'
    jsonEncoded = json.dumps(contents, sort_keys=True, indent=2, separators=(',', ': '))

    f.seek(0)
    f.truncate()
    f.write(jsonEncoded)
    f.close()

class AtlasGen:
  def getSize(self, data):
    try:
      i = Image.open(data)
      return i.size
    except:
      return None

  #this will always produce squares which may not be the most efficient
  #for 7 images it'll create a 3x3 square leaving two "blank" spaces
  #instead of a more efficient 4x2, I'll think of something someday
  def getDimensions(self, size, count):
    d = 1
    dim = 1
    while dim < count:
      d += 1
      dim = d * d
    if size * d > 4096:
      raise Exception('Atlas will be too large for Metal probably.')
    return (size * d, size * d)
  
  def makeAtlas(self, data):
    size = self.getSize(data[0])

    if not size:
      raise Exception('no image data')
      return None
    elif size[0] != size[1]:
      raise Exception('this was only (poorly) designed for square images')
      return None

    s = size[0]
    dimensions = self.getDimensions(s, len(data))
    cat = Image.new('RGBA', dimensions)

    x = 0
    y = 0
    for i in data:
      image = Image.open(i)

      if x * s >= dimensions[0]:
        y += 1
        x = 0
       
      cat.paste(image, (x * s, y * s))

      x += 1
    return cat

def main():
  if len(sys.argv) <= 2:
    print(sys.argv[0] + " xcassetsIn xcassetsOut")
    return

  fm = FileManager(sys.argv[1], sys.argv[2])
  if not fm.updateRequired():
    print('no update needed')
    return
  
  (size2data, size3data)= fm.getImageData()
  size2folders = fm.filterByFolder(size2data)
  size3folders = fm.filterByFolder(size3data)

  ag = AtlasGen()

  images2 = {}
  for (k, v) in size2folders.iteritems():
    images2[k] = ag.makeAtlas(v)
  
  images3 = {}
  for (k, v) in size3folders.iteritems():
    images3[k] = ag.makeAtlas(v)

  fm.deleteOldData()

  for (k, v) in images2.iteritems():
    fm.saveImageData(k, v, '2x')
  for (k, v) in images3.iteritems():
    fm.saveImageData(k, v, '3x')


if __name__ == '__main__':
  main()

