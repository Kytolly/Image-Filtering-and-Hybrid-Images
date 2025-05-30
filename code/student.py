# Project Image Filtering and Hybrid Images Stencil Code
# Based on previous and current work
# by James Hays for CSCI 1430 @ Brown and
# CS 4495/6476 @ Georgia Tech
import numpy as np
from numpy import pi, exp, sqrt
from skimage import io, img_as_ubyte, img_as_float32
from skimage.transform import rescale
import math

def my_imfilter(image, filter):
  """
  Your function should meet the requirements laid out on the project webpage.
  Apply a filter to an image. Return the filtered image.
  Inputs:
  - image -> numpy nd-array of dim (m, n, c)
  - filter -> numpy nd-array of odd dim (k, l)
  Returns
  - filtered_image -> numpy nd-array of dim (m, n, c)
  Errors if:
  - filter has any even dimension -> raise an Exception with a suitable error message.
  """
#####################################################################################################
#                                            Your Code                                              #
#####################################################################################################
  image_height, image_width = image.shape[:2]
  filter_height, filter_width = filter.shape
  num_channels = 1 if image.ndim == 2 else image.shape[2]

  # Calculate padding amounts
  pad_height = filter_height // 2
  pad_width = filter_width // 2
  padded_image = np.pad(image, ((pad_height, pad_height), (pad_width, pad_width), (0, 0) if num_channels > 1 else (0, 0)), mode='reflect')

  # filter process: convolution
  filtered_image = np.zeros_like(image)
  flipped_filter = np.flip(filter, axis=(0, 1))
  for c in range(num_channels):
      for i in range(image_height):
          for j in range(image_width):
              image_patch = padded_image[i:i+filter_height, j:j+filter_width, c] if num_channels > 1 else padded_image[i:i+filter_height, j:j+filter_width]
              
              filtered_image[i, j, c] = np.sum(image_patch * flipped_filter) if num_channels > 1 else np.sum(image_patch * flipped_filter)
#####################################################################################################
#                                               End                                                 #
#####################################################################################################
  return filtered_image


def gen_hybrid_image(image1, image2, cutoff_frequency):
  """
   Inputs:
   - image1 -> The image from which to take the low frequencies.
   - image2 -> The image from which to take the high frequencies.
   - cutoff_frequency -> The standard deviation, in pixels, of the Gaussian
                         blur that will remove high frequencies.

   Task:
   - Use my_imfilter to create 'low_frequencies' and 'high_frequencies'.
   - Combine them to create 'hybrid_image'.
  """

  assert image1.shape[0] == image2.shape[0]
  assert image1.shape[1] == image2.shape[1]
  assert image1.shape[2] == image2.shape[2]

  # Steps:
  # (1) Remove the high frequencies from image1 by blurring it. The amount of
  #     blur that works best will vary with different image pairs
  # generate a 1x(2k+1) gaussian kernel with mean=0 and sigma = s, see https://stackoverflow.com/questions/17190649/how-to-obtain-a-gaussian-filter-in-python
  s, k = cutoff_frequency, int(cutoff_frequency*2)
  probs = np.asarray([exp(-z*z/(2*s*s))/sqrt(2*pi*s*s) for z in range(-k,k+1)], dtype=np.float32)
  kernel = np.outer(probs, probs)
  
  #####################################################################################################
  #                                            Your Code                                              #
  #####################################################################################################
  # Your code here:
  # low_frequencies = None # Replace with your implementation
  low_frequencies = my_imfilter(image1, kernel)

  # (2) Remove the low frequencies from image2. The easiest way to do this is to
  #     subtract a blurred version of image2 from the original version of image2.
  #     This will give you an image centered at zero with negative values.
  # Your code here #
  # high_frequencies = None # Replace with your implementation
  image2_low_frequencies = my_imfilter(image2, kernel)
  high_frequencies = image2 - image2_low_frequencies

  # (3) Combine the high frequencies and low frequencies
  # Your code here #
  # hybrid_image = None
  hybrid_image = low_frequencies + high_frequencies

  # (4) At this point, you need to be aware that values larger than 1.0
  # or less than 0.0 may cause issues in the functions in Python for saving
  # images to disk. These are called in proj1_part2 after the call to 
  # gen_hybrid_image().
  # One option is to clip (also called clamp) all values below 0.0 to 0.0, 
  # and all values larger than 1.0 to 1.0.
  hybrid_image = np.clip(hybrid_image, 0, 1)
#####################################################################################################
#                                               End                                                 #
#####################################################################################################

  return low_frequencies, high_frequencies, hybrid_image

def vis_hybrid_image(hybrid_image):
  """
  Visualize a hybrid image by progressively downsampling the image and
  concatenating all of the images together.
  """
  scales = 5
  scale_factor = [0.5, 0.5, 1]
  padding = 5
  original_height = hybrid_image.shape[0]
  num_colors = 1 if hybrid_image.ndim == 2 else 3

  output = np.copy(hybrid_image)
  cur_image = np.copy(hybrid_image)
  for scale in range(2, scales+1):
    # add padding
    output = np.hstack((output, np.ones((original_height, padding, num_colors),
                                        dtype=np.float32)))
    # downsample image
    cur_image = rescale(cur_image, scale_factor, mode='reflect')
    # pad the top to append to the output
    pad = np.ones((original_height-cur_image.shape[0], cur_image.shape[1],
                   num_colors), dtype=np.float32)
    tmp = np.vstack((pad, cur_image))
    output = np.hstack((output, tmp))
  return output

def load_image(path):
  return img_as_float32(io.imread(path))

def save_image(path, im):
  return io.imsave(path, img_as_ubyte(im.copy()))
