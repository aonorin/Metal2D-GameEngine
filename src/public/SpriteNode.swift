//
//  Sprite.swift
//  MKTest
//
//  Created by Anthony Green on 12/30/15.
//  Copyright © 2015 Anthony Green. All rights reserved.
//

import Foundation
import Metal
import MetalKit

/**
 A `SpriteNode` is a node that can be rendered with a `Texture`. The applied texture can also be blended with a color.
 */
public class SpriteNode: Node, Renderable {
  public var color: UIColor

  public var texture: Texture?

  let vertexBuffer: MTLBuffer
  let indexBuffer: MTLBuffer
  let uniformBufferQueue: BufferQueue

  public var isVisible = true

  /**
   Designated initializer. Creates a new sprite object using an existing `Texture`.
   
   - discussion: The size should probably be the same as the texture size.

   - parameter texture: The texture to apply to the node.
   - parameter color:   The color to blend with the texture.
   - parameter size:    The size of node.

   - returns: A new instance of `SpriteNode`.
   */
  public required init(texture: Texture, color: UIColor, size: CGSize) {
    let (vertexBuffer, indexBuffer) = SpriteNode.setupBuffers([Quad.spriteRect(texture.frame)], device: Device.shared.device)

    self.vertexBuffer = vertexBuffer
    self.indexBuffer = indexBuffer
    self.uniformBufferQueue = BufferQueue(device: Device.shared.device, dataSize: sizeof(Uniforms))

    self.texture = texture
    self.color = color

    super.init(size: texture.size)
  }

  /**
   Convenience initializer.
   
   - discussion: This initializer sets the color property to white.

   - parameter texture: The texture to apply to the node.
   - parameter size:    The size of the node.

   - returns: A new instance of `SpriteNode`.
   */
  public convenience init(texture: Texture, size: CGSize) {
    self.init(texture: texture, color: .whiteColor(), size: size)
  }

  /**
   Convenience initializer. 
   
   - discussion: This creates a node with the same size as the texture as well as defaulting the color to white.

   - parameter texture: The texture to apply to the node.

   - returns: A new instance of `SpriteNode`.
   */
  public convenience init(texture: Texture) {
    self.init(texture: texture, color: .whiteColor(), size: texture.size)
  }

  /**
   Convenience initializer. 
   
   - discussion: This should really only be used for prototyping as this is the slowest and most memory intensive version.
                 It's pretty much used the same as `UIImage(named:)`. Unlike `UIImage`, however, it will force load an error image in the case 
                 that the given image name does not exist. Defaults size to image size and color to white.

   - parameter named: The name of the texture/image to be used.

   - returns: A new instance of `SpriteNote`.
   */
  public convenience init(named: String) {
    self.init(texture: Texture(named: named))
  }
}