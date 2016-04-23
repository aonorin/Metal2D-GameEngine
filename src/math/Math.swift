//
//  Math.swift
//  GameEngine
//
//  Created by Anthony Green on 4/10/16.
//  Copyright © 2016 Anthony Green. All rights reserved.
//

import Foundation

public final class Math {
  public static func degreesToRadians(d: Float) -> Float {
    return (Float(M_PI) / 180.0) * d
  }
}