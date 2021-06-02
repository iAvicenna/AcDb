#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 16:52:08 2021

@author: iavicenna
"""

def deep_eq(_v1, _v2):
  """
  Tests for deep equality between two python data structures recursing
  into sub-structures if necessary. Works with all python types including
  iterators and generators. This function was dreampt up to test API responses
  but could be used for anything. Be careful. With deeply nested structures
  you may blow the stack.

  Information: from samuraisam/deep_eq.py github, modified for compatibility
  to python 3
  """
  import operator

  def _deep_dict_eq(d1, d2):
    k1 = sorted(d1.keys())
    k2 = sorted(d2.keys())
    if k1 != k2: # keys should be exactly equal
      return False
    return sum(deep_eq(d1[k], d2[k]) for k in k1) == len(k1)

  def _deep_iter_eq(l1, l2):
    if len(l1) != len(l2):
      return False
    return sum(deep_eq(v1, v2) for v1, v2 in zip(l1, l2)) == len(l1)

  op = operator.eq
  c1, c2 = (_v1, _v2)

  # guard against strings because they are also iterable
  # and will consistently cause a RuntimeError (maximum recursion limit reached)
  for t in [str]:
    if isinstance(_v1, t):
      break
  else:
    if isinstance(_v1, dict):
      op = _deep_dict_eq
    else:
      try:
        c1, c2 = (list(iter(_v1)), list(iter(_v2)))
      except TypeError:
        c1, c2 = _v1, _v2
      else:
        op = _deep_iter_eq

  return op(c1, c2)