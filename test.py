from PIL import Image
import matplotlib.pyplot as plt
img=Image.open('./download/wordcloud/BV16i4y1A7Ho_wc.png')
plt.figure("dog")
plt.imshow(img)
plt.show()
