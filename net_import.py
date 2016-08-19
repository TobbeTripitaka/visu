







def make_section(data, lons, lats, degree=180):
	'''
	data is polar array
	lons and latitude arrays with grid
	degree is a positive longitude >0 and >=180
	
	'''
	
	degree = round(degree, 1)
	lons = np.round(lons, 1)
	
	print 'degree ', degree
	lon_index = np.where(lons==degree)[0]
	lon_index_180 = np.where(lons==(degree-180))[0]
	
	print 'lon index is:', lon_index, type(lon_index)
	print 'lon 180 index is:', lon_index_180, type(lon_index_180)
	
	sec_e = np.rot90(data[:,lon_index].squeeze(),k=3)
	sec_w = np.fliplr(np.rot90(data[:,lon_index_180].squeeze(),k=3))
	
	section = np.concatenate((sec_e, sec_w), axis=1)
	
	return section




# an_model is initial array, ny and nx resolution
an_model = np.zeros((83, 451)) 
ny, nx = an_model.shape

print '3D start model', an_model.shape, type(an_model)

for layer in temp_layers:
	layer = 'data/AN1-Tc_depth_grd/' + layer
	
	nc_fid = Dataset(layer, 'r')
	nc_attrs, nc_dims, nc_vars = ncdump(nc_fid)
	# Extract data from NetCDF file

	lons = nc_fid.variables['x'][:]
	lats = nc_fid.variables['y'][:]
	temp = nc_fid.variables['z'][:]
		
	an_model =  np.dstack([an_model, temp])
	
	
#np.save("out.npy", A)	



# 
print '3D model  : ', an_model.shape, type(an_model)
print 'temp layer: ', temp.shape, type(temp)

print 'lons: ', lons.shape, type(lons)
print 'lats: ', lats.shape, type(lats)

#print 'lats', lats
#print 'lons', lons

min_t = np.nanmin(an_model)
max_t = np.nanmax(an_model)-200 #Tweek for better color map range 

print 'Temperature range from %s to %s ' %(min_t, max_t)

print lats

fig = plt.figure(num=None, figsize=(6, 6), dpi=200, edgecolor='k')
#fig.suptitle("Temperatures from S-velocities and 1D heat transfer function (An et al 2015)", fontsize=16)
section = make_section(an_model, lons=lons, lats=lats, degree=90.4)
im = plt.imshow(section, 
	vmin = min_t, vmax = max_t, 
	cmap = plt.cm.magma, 
	extent=[-90-max(lats),90+max(lats),100,0],
	aspect=0.2,
	interpolation='nearest')
	

fig.colorbar(im, orientation='horizontal',fraction=0.046, pad=0.04)	

#axes = plt.gca()
#axes.set_ylim([-100,0])
#axes.set_xlim([-180,180])

#extent = [-18, 52, -38, 38] # [left, right, bottom, top]
m = Basemap(projection='merc', llcrnrlon=extent[0], urcrnrlon=extent[1], llcrnrlat=extent[2], urcrnrlat=extent[3], resolution='c')
m.drawcountries() 
plt.imshow(im, extent=extent, alpha=0.6)
plt.show()


plt.show()