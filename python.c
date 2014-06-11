/* Basic Python structure:

def play():
    """ This returns 0, 1, or 2 and is the main entry point """
    return 0

def SkeletonAI():
    """ This is the most basic AI that showcase the rps library """
    currentTurn = rps.getTurn()
    
    if currentTurn:
        myMoveLastTurn = rps.myHistory(currentTurn)
        enemyMoveLastTurn = rps.enemyHistory(currentTurn)
    
    return (rps.enemyHistory(currentTurn) + 1) % 3

def isVerbose():
    """If True is returned, print the result of each trial."""
    return False
*/

#define HAVE_SSIZE_T
#include <Python.h>

extern int my_history[];
extern int opp_history[];

#define MYHISTORY    0
#define ENEMYHISTORY 1

int getHistory(int history, PyObject *args)
{
    // getHistory starts with 1 index
    
    int index;
    if (!PyArg_ParseTuple(args, "i", &index))
        return 0;	

    if (index == 0)                     // returns -1. getTurn() should be used to get current turn
        return PyLong_FromLong(-1);     // todo: raise errors
        
    if (index > my_history[0])          // returns -1. cannot get the history from the future (can also contain garbage)
        return PyLong_FromLong(-1);     // todo: raise errors

    if (index < 0)                      // returns -1.
        return PyLong_FromLong(-1);     // todo: raise errors

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

static PyObject *
rps_getTurn(PyObject *self, PyObject *args)
{
    return PyLong_FromLong(my_history[0]);
}

extern int biased_roshambo (double prob_rock, double prob_paper);
extern long random ();

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
    
    int result = biased_roshambo(prob_rock, prob_paper);
    
    /*//debug
    printf("%f %f", prob_rock, prob_paper);
    printf("result%i", result);
    getch();//*/
    
    return PyLong_FromLong(result);
}

static PyObject *
rps_random ()
{
    return PyLong_FromLong(random());
}

static PyMethodDef rpsMethods[] = {
    {"myHistory",  rps_myhistory, METH_VARARGS, "Returns player history.\nIndex 0 returns -1. You should use getTurn() to get current turn.\nIndex starts at 1."},
    {"enemyHistory",  rps_enemyhistory, METH_VARARGS, "Returns enemy history.\nIndex 0 returns -1. You should use getTurn() to get current turn.\nIndex starts at 1."},
    {"getTurn",  rps_getTurn, METH_VARARGS, "Returns current turn."},
    {"biased_roshambo",  rps_biased_roshambo, METH_VARARGS, "Returns 0, 1 or 2. Takes two double arguments: prob_rock and prob_paper"},
    {"random",  rps_random, METH_VARARGS, "Returns 0 to [maxrandom]."},
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
        yomiFunc = PyObject_GetAttrString(pModule, "play");
        /* yomiFunc is a new reference */
        if (!yomiFunc) {
            if (PyErr_Occurred())
                PyErr_Print();
            fprintf(stderr, "Cannot find function Play\n");
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
