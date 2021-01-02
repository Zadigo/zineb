from zineb.app import Zineb
from zineb.http.pipelines import Pipeline
from zineb.utils.general import download_image


# class SawFirst(Zineb):
#     start_urls = [
#         'https://www.sawfirst.com/kimberley-garner-booty-in-bikini-on-the-beach-in-barbados-2020-12-28.html'
#     ]

#     def start(self, response, **kwargs):
#         images = response.images

#         filtered_images = filter(lambda x: 'Kimbeley-Garner' in x, images)

#         def thumbnails(url):
#             if '-130x170.jpg' in url:
#                 return str(url).replace('-130x170.jpg', '.jpg')

#         filtered_images = map(thumbnails, filtered_images)
#         filtered_images = filter(lambda x: x is not None, filtered_images)
#         Pipeline(filtered_images, download_image)

# s = SawFirst()


urls = [
    'https://www.sawfirst.com/wp-content/uploads/2020/12/Kimbeley-Garner-901.jpg',
    'https://www.sawfirst.com/wp-content/uploads/2020/12/Kimbeley-Garner-909.jpg'
]

Pipeline(urls, download_image)
