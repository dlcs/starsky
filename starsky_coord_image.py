import PIL


image_path = ''.join([image_uri, '/full/full/0/default.jpg'])
r = requests.get(full_image)
image = Image.open(StringIO(r.content))
