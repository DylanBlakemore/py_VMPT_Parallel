#include <Python.h>
#include <numpy/arrayobject.h>
#include <math.h>
#include <stdio.h>

static int getListItemInt(PyObject* py_list, int index) {
    if(PyList_Check(py_list)) {
        return (int)PyInt_AsSsize_t(PyList_GetItem(py_list, index));
    } else {
        return -1;
    }
}

static int getMatrixRow(double* data, int row, int dims, double* entry) {
    for(int i = 0; i < dims; i++) {
        int index = row * dims + i;
        entry[i] = data[index];
    }
    return 0;
}

static double getEuclideanDistance(double* A, double* B) {
    double sqsum = 0;    
    for(int i = 0; i < 3; i++) {
        sqsum += pow(A[i] - B[i],2);
    }
    return sqrt(sqsum);
}

static PyObject* vmptlib_getSmallestRegion(PyObject* self, PyObject* args) {
    int num_lines;                  // the total number of LOR's in the frame
    PyObject* line_indices;         // (npoints,1) list of ints; ID's of lines along which points lie
    PyObject* point_regions;        // (npoints,1) list of ints; indices into Voronoi regions
    PyObject* regions;              // (nregions,*) list of list of ints; indices into vertices
    PyArrayObject* vertices;             // (nvertices,3) ndarray of doubles; co-ords of vertices
    /* variables used throughout the function */
    int line_counter    = 0;
    int point_counter   = 0;
    double min_volume   = 100000.0;
    int num_points;
    int line_id;
    /* Verify argument data types */
    if (!PyArg_ParseTuple(args, "iOOOO!", &num_lines, 
                                         &line_indices, 
                                         &point_regions,
                                         &regions,
                                         &PyArray_Type, &vertices))
        return NULL;
    
    double* vertex_data = (double*)PyArray_DATA(vertices);
    num_points = (int)PyList_Size(line_indices);    // the total number of seed points
    PyObject* output_indices = PyList_New(num_lines);
    PyObject* output_volumes = PyList_New(num_lines);

    while(point_counter < num_points) {
        line_id = getListItemInt(line_indices, point_counter);
        if(line_id == line_counter) {
            
            int region_index        = getListItemInt(point_regions, point_counter);    // the index of the Voronoi region
            PyObject* vertex_list   = PyList_GetItem(regions, region_index);      // a list of the  vertices
            int num_vertices        = (int)PyList_Size(vertex_list);                   // total number of vertices     
            double centroid[3]      = {0.0, 0.0, 0.0};
            
            for(int vertex_i = 0; vertex_i < num_vertices; vertex_i++) {
                int vertex_row = getListItemInt(vertex_list, vertex_i);         // vertex entry in vertices object
                if(vertex_row != -1) {
                    double vertex[3];
                    getMatrixRow(vertex_data, vertex_row, 3, vertex);
                    for(int dim = 0; dim < 3; dim++)
                        centroid[dim] = centroid[dim] + vertex[dim] / (float)num_vertices;
                }          
            }
             
            double region_volume    = 0;   
            for(int vertex_i = 0; vertex_i < num_vertices; vertex_i++) {
                int vertex_row = getListItemInt(vertex_list, vertex_i);         // vertex entry in vertices object
                double vertex[3];     
                if(vertex_row != -1) {           
                    getMatrixRow(vertex_data, vertex_row, 3, vertex);   
                    double distance = getEuclideanDistance(vertex, centroid);
                    region_volume = region_volume +  distance/num_vertices;
                
                } else {
                    region_volume = 100000.0;
                    break;                
                }
            }
            
            if( region_volume <= min_volume) {
                PyObject* py_index = Py_BuildValue("i",point_counter);
                PyObject* py_volume = Py_BuildValue("f", region_volume);
                PyList_SetItem(output_indices, line_id, py_index);
                PyList_SetItem(output_volumes, line_id, py_volume);
                min_volume = region_volume;
            }
        
            point_counter++;
        } else {
            min_volume = 100000.0;
            line_counter++;
        }
    }

    return Py_BuildValue("OO",output_indices,output_volumes);
}

/* Documentation strings */
static char module_docstring[] =
    "This module provides methods written in C for the VMPT program.";
static char getSmallestRegion_docstring[] = 
    "Get the smallest Voronoi region per line of response.";

/* Add all methods */
static PyMethodDef vmptlib_methods[] = {
    {"getSmallestRegion", vmptlib_getSmallestRegion, METH_VARARGS, getSmallestRegion_docstring},
    {NULL, NULL, 0, NULL}
};

/* Entry point for Python script */
PyMODINIT_FUNC initvmptlib(void) {
    PyObject *m = Py_InitModule3("vmptlib", 
                    vmptlib_methods,
                   module_docstring);
    if(m == NULL)
        return;

    import_array();
}