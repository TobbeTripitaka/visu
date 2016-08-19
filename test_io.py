#!/usr/bin/python
import os, sys, getopt, tarfile


import numpy as np
import numpy.ma as ma

from netCDF4 import Dataset 

import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap, addcyclic, shiftgrid, cm


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
        """
        Prints attributes

        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        
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
        tar.close()
    elif (f_name.endswith("tar")):
        tar = tarfile.open(f_name, "r:")
        tar.extractall(path=os.path.dirname(f_name))
        tar.close()		
    else:
        pass
    files_in_folder = os.listdir(f_name)
    layer_files = [i for i in files_in_folder if (i.endswith('.nc') or (i.endswith('.grd')))]
    return layer_files
     


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
	
	
def array2images(data_cube, file_list, img_color_map):
    max_cmap = np.amax(data_cube)
    cmap=plt.get_cmap(img_color_map)
    img_dir = 'img'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
       
    print 'Size of dataset preroll: ', data_cube.shape   
    data_cube = np.swapaxes(data_cube, 0, 2)
    print 'Size of dataset postroll: ', data_cube.shape
    
    for layer_index in xrange(0, 51, 1):
        print data_cube[layer_index].shape
        plt.imshow(data_cube[layer_index]) #Needs to be in row,col order
        plt.savefig('%s/%s.png' % (img_dir, file_list[layer_index]), bbox_inches='tight',transparent=True)
        if verbose:
            print 'Saved %s/%s.png' % (img_dir, file_list[layer_index])
     	
#Todo:

# Wrong colormap (jet?!)
# Check if resolution is ok
# Export fil med positions
# Check for nan and convert to alpha
#Export positions
	
	
	
### Start here...
if __name__ == "__main__":
    input_dir, img_color_map, verbose, save_array = main(sys.argv[1:])

file_list = data_to_import(input_dir)

data_cube, lons, lats = import_layers(
                        path =input_dir, 
                        in_layers = file_list, 
                        variables = ('x','y','z'))

array2images(data_cube, file_list, img_color_map)


if save_array:
    print 'saving array to %sdata.npy' %input_dir
    data_cube.dump('%sdata.npy' %input_dir)

### return info
if verbose:
    print
    print 'Dir:', input_dir
    #print 'List of layers: ', data_to_import(input_dir)
    print 'Number of layers: ', len(data_to_import(input_dir))
    print 'Size of dataset: ', data_cube.shape
    print 'lats: ', min(lats), 'to', max(lats)
    print 'lons: ', min(lons), 'to', max(lons)







    
#    ny, nx = model.shape	

