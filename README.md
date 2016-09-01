# visu
Some simple scripts to convert .grd files to multiple .png for visualisation. Also code to crop a large dataset from reference .csv textfile. 

There are some dependencies. However all are packages availoble from conda. Basemap can be commented out if output don't need to be projected.

E.g. grid files in folder data/ output images in colormap 'magma'. Verbose would be useful
Run:
```
$ python grd2img.py -i data/ -c magma -v True
```

There are anumber of arguments

-i set input folder or tarball or zipped tarball
-c set colormap of choice. Default is 'gray'
-h for help
-v verbose?
-s save array as np binary

Also check the function array2images() There are some useful settings to manipulate the output

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
