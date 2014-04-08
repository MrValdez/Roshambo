#define HAVE_SSIZE_T
#include <Python.h>

extern int my_history[];
extern int opp_history[];

#define MYHISTORY    0
#define ENEMYHISTORY 1

int getHistory(int history, PyObject *args)
{
    int index;
    if (!PyArg_ParseTuple(args, "i", &index))
        return 0;	

    if (index > my_history[0])
        return 0;

    if (history == MYHISTORY)
        return PyLong_FromLong(my_history[index]);
    else if (history == ENEMYHISTORY)
        return PyLong_FromLong(opp_history[index]);
}

static PyObject *
rps_myhistory(PyObject *self, PyObject *args)
{        
    return getHistory(MYHISTORY, args);
}

static PyObject *
rps_enemyhistory(PyObject *self, PyObject *args)
{
    return getHistory(ENEMYHISTORY, args);
}

extern int biased_roshambo (double prob_rock, double prob_paper);

static PyObject *
rps_biased_roshambo(PyObject *self, PyObject *args)
{
    double prob_rock;
    double prob_paper;
    if (!PyArg_ParseTuple(args, "dd", &prob_rock, &prob_paper))     //d refers to double, not decimal
    {
        printf ("biasedRoshambo received invalid arguments");
        exit(1);
        return -1;  //todo: raise error	
    }
    
    /*//debug
    printf("%f %f", prob_rock, prob_paper);
    getch();*/
    
    int result = biased_roshambo(prob_rock, prob_paper);
    return PyLong_FromLong(result);
}

static PyMethodDef rpsMethods[] = {
    {"myHistory",  rps_myhistory, METH_VARARGS, "Returns player history. Index 0 returns current turn. Index 1 to trials contains the move used in that turn"},
    {"enemyHistory",  rps_enemyhistory, METH_VARARGS, "Returns enemy history. Index 0 returns current turn. Index 1 to trials contains the move used in that turn"},
    {"biased_roshambo",  rps_biased_roshambo, METH_VARARGS, "Returns 0, 1 or 2. Takes two double arguments: prob_rock and prob_paper"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef rpsModule = {
   PyModuleDef_HEAD_INIT,
   "rps",   /* name of module */
   0, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   rpsMethods,
   NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit_rps(void)
{
    return PyModule_Create(&rpsModule);
}

PyObject *pModule, *yomiFunc;
int initPython(int argc, char *argv[])
{
    PyObject *pName;
    
    int i;

    PyImport_AppendInittab("rps", &PyInit_rps);
    Py_SetProgramName(argv[0]);
    Py_Initialize();
    pName = PyUnicode_FromString("yomi");
    /* Error checking of pName left out */

    PyImport_ImportModule("rps");
    pModule = PyImport_Import(pName);
    Py_DECREF(pName);
    
    if (pModule != NULL) {       
        yomiFunc = PyObject_GetAttrString(pModule, "yomi");
        /* yomiFunc is a new reference */
        if (!yomiFunc) {
            if (PyErr_Occurred())
                PyErr_Print();
            fprintf(stderr, "Cannot find function \"%s\"\n", argv[2]);
            return 1;
        }
    }
    else {
        PyErr_Print();
        fprintf(stderr, "Failed to load \"%s\"\n", argv[1]);
        return 1;
    }
    
    return 0;
}

int isVerbose()
{
    PyObject *pFunc = PyObject_GetAttrString(pModule, "isVerbose");
    if (!pFunc) {
        if (PyErr_Occurred())
            PyErr_Print();
        fprintf(stderr, "Cannot find function \"isVerbose\"");
        return -1;
    }
    else
    {
        PyObject *pValue = PyObject_CallObject(pFunc, 0);
        int result;
        
        if (pValue != NULL) {
            result = PyLong_AsLong(pValue);
            Py_DECREF(pValue);
        }
        
        return result;
    }
}     

extern int yomiVariable1;

int python()
{
  int result = -1;
  if (PyCallable_Check(yomiFunc)) 
  {
    PyObject *pValue;
    
    // Parse arguments
    PyObject *pArgs = PyTuple_New(1);
    
    int index = 0;
    pValue = PyLong_FromLong(yomiVariable1);
    if (!pValue) {
        Py_DECREF(pArgs);
        Py_DECREF(pModule);
        fprintf(stderr, "Cannot convert argument\n");
        return -1;
    }
    PyTuple_SetItem(pArgs, index, pValue);

    // Call the function
    pValue = PyObject_CallObject(yomiFunc, pArgs);
    Py_DECREF(pArgs);

    // Checks
    if (pValue != NULL) {
        result = PyLong_AsLong(pValue);
        Py_DECREF(pValue);
    }
    else {
        Py_DECREF(yomiFunc);
        Py_DECREF(pModule);
        PyErr_Print();
        fprintf(stderr,"Call failed\n");
        exit(-1);
        return 0;
    }
   }
    
   return result;
}

void exitPython()
{
    Py_XDECREF(yomiFunc);
    Py_DECREF(pModule);

    Py_Finalize();
    return 0;
}
