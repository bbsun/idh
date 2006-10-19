/****************************************************************************
Copyright (c) 2006, Colorado School of Mines and others. All rights reserved.
This program and accompanying materials are made available under the terms of
the Common Public License - v1.0, which accompanies this distribution, and is 
available at http://www.eclipse.org/legal/cpl-v10.html
****************************************************************************/
package lcc;

import edu.mines.jtk.dsp.*;
import edu.mines.jtk.opt.*;
import edu.mines.jtk.util.*;
import static edu.mines.jtk.util.MathPlus.*;

/**
 * Filters displacements to minimize strain.
 * Minimizes J(u) = u* Q u + s u* D* D u.
 * @author Dave Hale, Colorado School of Mines
 * @version 2006.10.19
 */
public class DisplacementFilter {

  /**
   * Construct a displacement filter with specified parameters.
   * @param smooth the amount of smoothing.
   */
  public DisplacementFilter(double smooth) {
  }

  /**
   * Applies this filter for the specified quadratic fit.
   * @param q coefficients for the quadratic fit.
   *  q[0] contains a measure of quality between 0 and 1; and
   *  q[1], q[2], and q[3] contain coefficients of the matrix Q:
   *  <pre>
   *    Q = | q[1]  q[2] |
   *        | q[2]  q[3] |
   *  </pre>
   * @param u the displacements (u1,u2) = (u[0],u[1]) to be filtered.
   */
  public void apply(float[][][] q, float[][][] u) {
  }

  ///////////////////////////////////////////////////////////////////////////
  // private


  // Vector of displacements u.
  private static class UVect extends ArrayVect3f {
    UVect(float[][][] q) {
      _q = q;
    }
    public void multiplyInverseCovariance() {
      float[][][] u = getData();
      float[][] u1 = u[0];
      float[][] u2 = u[1];
      float[][] q0 = _q[0];
      float[][] q1 = _q[1];
      float[][] q2 = _q[2];
      float[][] q3 = _q[3];
      int n1 = u1[0].length;
      int n2 = u1.length;
      for (int i2=0; i2<n2; ++i2) {
        for (int i1=0; i1<n1; ++i1) {
          float u1i = u1[i2][i1];
          float u2i = u2[i2][i1];
          float q0i = q0[i2][i1];
          float q1i = q1[i2][i1];
          float q2i = q2[i2][i1];
          float q3i = q3[i2][i1];
          u1[i2][i1] = q0i*(q1i*u1i+q2i*u2i);
          u2[i2][i1] = q0i*(q2i*u1i+q3i*u2i);
        }
      }
    }
    public double magnitude() {
      float[][][] u = getData();
      float[][] u1 = u[0];
      float[][] u2 = u[1];
      float[][] q0 = _q[0];
      float[][] q1 = _q[1];
      float[][] q2 = _q[2];
      float[][] q3 = _q[3];
      int n1 = u1[0].length;
      int n2 = u1.length;
      double sum = 0.0;
      for (int i2=0; i2<n2; ++i2) {
        for (int i1=0; i1<n1; ++i1) {
          float u1i = u1[i2][i1];
          float u2i = u2[i2][i1];
          float q0i = q0[i2][i1];
          float q1i = q1[i2][i1];
          float q2i = q2[i2][i1];
          float q3i = q3[i2][i1];
          float u1t = q0i*(q1i*u1i+q2i*u2i);
          float u2t = q0i*(q2i*u1i+q3i*u2i);
          sum += u1i*u1t+u2i*u2t;
        }
      }
      return sum;
    }
    private float[][][] _q;
  }

  // Smoothing transform u = S*v and its transpose.
  private static class VSmooth implements LinearTransform {
    public void forward(Vect data, VectConst model) {
      float[][][] v = ((ArrayVect3f)model).getData();
      float[][] v1 = v[0];
      float[][] v2 = v[1];
      float[][][] u = ((ArrayVect3f)data).getData();
      float[][] u1 = u[0];
      float[][] u2 = u[1];
      _df.applyInverse(v1,u1);
      _df.applyInverse(v2,u2);
    }
    public void addTranspose(VectConst data, Vect model) {
      float[][][] v = ((ArrayVect3f)model).getData();
      float[][] v1 = v[0];
      float[][] v2 = v[1];
      float[][][] u = ((ArrayVect3f)data).getData();
      float[][] u1 = u[0];
      float[][] u2 = u[1];
      int n1 = u1[0].length;
      int n2 = u1.length;
      float[][] vt = new float[n2][n1];
      _df.applyInverseTranspose(u1,vt);
      Array.add(vt,v1,v1);
      _df.applyInverseTranspose(u2,vt);
      Array.add(vt,v2,v2);
    }
    public void inverseHessian(Vect model) {
    }
    public void adjustRobustErrors(Vect dataError) {
    }

    private DifferenceFilter _df = new DifferenceFilter();
  }
}