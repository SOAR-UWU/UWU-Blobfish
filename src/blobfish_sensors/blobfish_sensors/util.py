import numpy as np
from scipy.spatial.transform import Rotation


# Stolen from https://scikit-surgerycore.readthedocs.io/en/latest/module_ref.html
def average_quaternions(quaternions: np.ndarray):
    """
    Calculate average quaternion

    :params quaternions: is a Nx4 np matrix and contains the quaternions
        to average in the rows.
        The quaternions are arranged as (w,x,y,z), with w being the scalar

    :returns: the average quaternion of the input. Note that the signs
        of the output quaternion can be reversed, since q and -q
        describe the same orientation
    """

    # Number of quaternions to average
    samples = quaternions.shape[0]
    mat_a = np.zeros(shape=(4, 4), dtype=np.float64)

    for i in range(0, samples):
        quat = quaternions[i, :]
        # multiply quat with its transposed version quat' and add mat_a
        mat_a = np.outer(quat, quat) + mat_a

    # scale
    mat_a = (1.0 / samples) * mat_a
    # compute eigenvalues and -vectors
    eigen_values, eigen_vectors = np.linalg.eig(mat_a)
    # Sort by largest eigenvalue
    eigen_vectors = eigen_vectors[:, eigen_values.argsort()[::-1]]
    # return the real part of the largest eigenvector (has only real part)
    return np.real(np.ravel(eigen_vectors[:, 0]))


def remove_gravity_from_accel(rot: Rotation, g, x, y, z):
    """Remove effect of gravity on IMU acceleration."""
    g_vec = np.array([0, 0, -g])
    g_vec = rot.apply(g_vec, inverse=True)
    gx, gy, gz = g_vec
    return x - gx, y - gy, z - gz
