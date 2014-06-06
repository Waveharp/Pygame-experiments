How tmxloader.py works

	from pytmx import tmxloader
	tmxdata = tmxloader.load_pygame("map.tmx")
		def load_pygame(): # on line 337 of tmxloader.py
			# load_pygame does:
			tmxdata = pytmx.TiledMap(filename)
				# which is a call to class TiledMap, line 151 of pytmx.py

			_load_images_pygame(tmxdata, None, *args, **kwargs)
				# which is a call to the function on line 250 of tmxloader

			return tmxdata

			# so the images have been loaded

	# Then
	# When you want to draw tiles, you simply call "getTileImage":
    image = tmxdata.get_tile_image(x coord, y coord, layer number)
    	# tmxdata is a TiledMap(filename) object
    	# def get_tile_image line 233 of pytmx

    screen.blit(image, position)
