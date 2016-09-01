#!/usr/bin/python
import os, sys, getopt, tarfile

import numpy as np
#import numpy.ma as ma

from netCDF4 import Dataset
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid, cm

def main(argv):
    '''
    Get command line arguments. Name input dataset and colormap for images. 
    
    Parameters from shell
    ----------	
    "-i" or "data=" name path to directory with .nc or .grd files
    "-o" or "color=" naame the colormap for output images. Grey is default.
    "-h" some help
    "-v" verbose boolean global variable
    "-s" save array to np-file 
    Returns
    -------
    Returns strings with filename, colormap and boolean verbose setting. 
    '''
    def str2bool(thoughts): 
        '''
        Setting in string variable to boolean
        '''
        if type(thoughts) == bool:
            return thoughts
        else:   
            return thoughts.lower() in ("yes", "true", "t", "1", "oui")
     
    # Set defaults: 
    input_dir = ''
    img_color_map = 'gray'
    verbose = False
    save_array = False
    
    try:
        opts, args = getopt.getopt(argv,"hi:c:v:s:",["data=", "color=", "verbose=", "save_array="])
    except getopt.GetoptError:
        print 'test.py -i <input folder> -c <output_color> -v <verbose> -s <save array>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print '''
            net_import.py -i <input_folder = %s> -c <color_map> -v <verbose=%s -s <save=%s>>
            ''' %(img_color_map, verbose, save_array) 
            sys.exit()
        elif opt in ("-i", "--ifile"): 
            input_dir = arg
        elif opt in ("-c", "--color"):
            img_color_map = arg
        elif opt in ("-v", "--verbose"): 
            verbose = arg
        elif opt in ("-s", "--save_array"): 
            save_array = arg
    return (input_dir, img_color_map, str2bool(verbose), str2bool(save_array))


def ncdump(nc_fid):
    '''
    Read dimensions, variables and their attribute information in netCDF4. files

    Parameters
    ----------
    nc_fid : 
        A GMT .grd file or another netCDF4 dataset

    global boolean variable verbose used

    Returns
    -------
    nc_attrs : list
        A Python list of the NetCDF file global attributes
    nc_dims : list
        A Python list of the NetCDF file dimensions
    nc_vars : list
        A Python list of the NetCDF file variables
    '''
    def print_ncattr(key):
        '''
        Prints attributes

        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
       '''
        
        try:
            print "\t\ttype:", repr(nc_fid.variables[key].dtype)
            for ncattr in nc_fid.variables[key].ncattrs():
                print '\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr))
        except KeyError:
            print "\t\No variable attributes" % key
    nc_attrs = nc_fid.ncattrs()
    if verbose:
        print "Attributes:"
        for nc_attr in nc_attrs:
            print '\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr))
    nc_dims = [dim for dim in nc_fid.dimensions] 

    if verbose:
        print "Dimensions:"
        for dim in nc_dims:
            print "\tName:", dim 
            print "\t\tsize:", len(nc_fid.dimensions[dim])
            print_ncattr(dim)

    nc_vars = [var for var in nc_fid.variables] 
    if verbose:
        print "Variables:"
        for var in nc_vars:
            if var not in nc_dims:
                print '\tName:', var
                print "\t\tdimensions:", nc_fid.variables[var].dimensions
                print "\t\tsize:", nc_fid.variables[var].size
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars

def data_to_import(f_name):
    '''
    Make list of grd files in directory. If it's not unzipped, open. 
    Parameters
    ----------
    f_name: string
        Path where (only) grd files are stored e.g data/ or .tar or .tar.gz ball
    '''
    if (f_name.endswith("tar.gz")): 
        tar = tarfile.open(f_name, "r:gz")
        tar.extractall(path=os.path.dirname(f_name))
        f_name = os.path.dirname(f_name) + '/'
        tar.close()
    elif (f_name.endswith("tar")):
        tar = tarfile.open(f_name, "r:")
        tar.extractall(path=os.path.dirname(f_name))
        f_name = os.path.dirname(f_name) + '/'
        tar.close()	
    elif (f_name.endswith("/")):   
        pass
    else:
        print 'Error: Input should be folder (end with / ) or tar-ball or zipped folder.'
        sys.exit(2)
    files_in_folder = os.listdir(f_name)
    layer_files = [i for i in files_in_folder if (i.endswith('.nc') or (i.endswith('.grd')))]
    return layer_files, f_name
     
def import_layers(path, in_layers,variables = ['x','y','z']):
    '''
    Read files defined in in_layers, add to numpy array
    Parameters
    ----------
    path: string
        path to folder/file
    in_layers: list
        list of filenames to import
    variables: list
        list of variable names
    
    Returns
    -------
    Numpy array of z values
    x array with x cell positions
    y array with y cell positions
    '''
    for layer in in_layers:
        nc_fid = Dataset(path + layer , 'r')
        nc_attrs, nc_dims, nc_vars = ncdump(nc_fid)
        z = nc_fid.variables[variables[2]][:] # eg z or data	
        if layer is not in_layers[0]:
            data_cube = np.dstack([data_cube, z])
        else:
            data_cube = z
            x = nc_fid.variables[variables[0]][:] # eg x or lon
            y = nc_fid.variables[variables[1]][:] # eg y or lat    
    return data_cube, x, y
	
def array2images(data_cube, file_list, img_color_map, lons, lats, 
    cube_swap= (0,2), 
    image_dir = 'img', 
    proj_it = True,
    proj_type = 'sptere',
    flip_flop = True,
    rotting = True,
    swip = True,
    exp_bar = True):
    '''
    Save array slices to images
    Parameters
    ----------
    data_cube: numpy array
        3D array to export
    file_list: list
        list with names to save. Lengh of list sets nr of exported files
    img_color_map: string
        Name of colormap to use. No path, e.g. 'magma' or 'cool'
    imf_dir: string
        path to exported files
    cube_swap : tuple
        swap of axes to slice cube in wanted diriection. E.g. (0,2). E.g (1,1) is no swap
    imgage_dir: string
        where to store figures
    proj_it: boolean
        Save as projected
    proj_type: string
        Projection
    rotting: boolean
        Rotate array?
    flip_flop: boolean
        Flip array?    
    swip: boolean
        swap array    
    exp_bar: boolean
        Export colorbar as image

    '''
    
    img_interpol = None # Interpolation?
    max_cmap = np.nanmax(data_cube)
    min_cmap =np.nanmin(data_cube)
    cmap=plt.get_cmap(img_color_map)

    if exp_bar:
        a = np.array([[min_cmap,max_cmap]])
        plt.figure(figsize=(9, 1.5))
        img = plt.imshow(a, cmap=img_color_map)
        plt.gca().set_visible(False)
        cax = plt.axes([0.1, 0.2, 0.8, 0.6])
        plt.colorbar(orientation="horizontal", cax=cax)
        plt.savefig('colorbar_%s.png' % img_color_map)
    
    
    plt.set_cmap(img_color_map)
    plt.axis('off')
    img_dir = image_dir
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    
    if flip_flop:
        data_cube = np.fliplr(data_cube)
    if rotting:
        data_cube = np.rot90(data_cube, 1)
    if swip:
        data_cube = np.swapaxes(data_cube, cube_swap[0], cube_swap[1]) # rotate to get orientation

    
    if proj_it:
        fig = plt.figure(figsize=(14,14))
        ny, nx = data_cube[1].shape   
        
        map = Basemap(projection='spstere', boundinglat=-60, lon_0=180, resolution='f')
        map.drawcoastlines(color='white', linewidth=2.0)
        map.drawparallels(np.arange(-80.,81.,30.))
        map.drawmeridians(np.arange(-180.,181.,30.))

        lons = np.linspace(min(lons), max(lons), nx)
        lats = np.linspace(min(lats), max(lats), ny)
    
    if verbose:
        print 'Saving images:'
    
    for layer_index in xrange(0, len(file_list), 1): ##### delete!!!!
        
 #       plt.clim(min_cmap,max_cmap)
       
        if verbose:
            print '\t%s/%s.png with shape %s' %(img_dir, file_list[layer_index], data_cube[layer_index].shape)

        if proj_it:
            plotdata = map.transform_scalar(data_cube[layer_index], lons, lats, nx, ny)
            img = map.imshow(plotdata, vmin = min_cmap, vmax = max_cmap, cmap = plt.cm.magma) #viridis
        else:    
            img = plt.imshow(data_cube[layer_index], interpolation=img_interpol) # T=Transpose
            
        plt.savefig('%s/%s.png' % (img_dir, file_list[layer_index]), 
            bbox_inches='tight', transparent=True)
    return  	



#Todo:

# Check if resolution is ok
# Export fil med positions
# Check for nan and convert to alpha
#Export positions
# Don't convert .tar and .gz correctly Maybe.

# print 'How many nan: ', data_cube[layer_index].size - np.count_nonzero(np.isnan(data_cube[layer_index]))

#        cb = fig.colorbar(im, orientation='horizontal',fraction=0.046, pad=0.04)
#        cb.ax.tick_params(labelsize=24)             
#        cb.ax.yaxis.set_tick_params(color='w')

	
	
	
### Start here...
if __name__ == "__main__":
    input_object, img_color_map, verbose, save_array = main(sys.argv[1:])

file_list, input_dir = data_to_import(input_object)

data_cube, lons, lats = import_layers(
                        path =input_dir, 
                        in_layers = file_list, 
                        variables = ('x','y','z'))

array2images(data_cube, file_list, img_color_map, lons, lats)



if save_array:
    print 'saving array to %sdata.npy' %input_dir
    data_cube.dump('%sdata.npy' %input_dir)

### return info
if verbose:
    print
    print 'Dir:', input_dir
    #print 'List of layers: ', data_to_import(input_dir)
    print 'Size of dataset: ', data_cube.shape
    print 'lats: ', min(lats), 'to', max(lats)
    print 'lons: ', min(lons), 'to', max(lons)
    print 'Data range: %g to %g' %(np.nanmin(data_cube), np.nanmax(data_cube)) 


text_file = open('extension.txt', 'w')
text_file.write('Imported layers: \n' +
        ','.join(map(str, file_list))+'\n\n' +
        'Size of dataset: ' + str(data_cube.shape) +
        'Lons: \n' + 
        ','.join(map(str, lons))+'\n\n' +
        'Lats: \n' +
        ','.join(map(str, lats))+'\n')
text_file.close()






    
#    ny, nx = model.shape	

