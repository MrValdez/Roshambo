//https://docs.python.org/3/extending/embedding.html#pure-embedding
#define HAVE_SSIZE_T
#include <Python.h>

#define trials 1
int my_history[trials+1];
int opp_history[trials+1];

void init()
{
    my_history[0] = 1;
    my_history[1] = 2;
}

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

static PyMethodDef rpsMethods[] = {
    {"myHistory",  rps_myhistory, METH_VARARGS, "Returns player history. Index 0 returns current turn. Index 1 to trials contains the move used in that turn"},
    {"enemyHistory",  rps_enemyhistory, METH_VARARGS, "Returns enemy history. Index 0 returns current turn. Index 1 to trials contains the move used in that turn"},
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

int
main(int argc, char *argv[])
{
    init();

    PyObject *pName, *pModule, *pDict, *pFunc;
    PyObject *pArgs, *pValue;
    int i;

    PyImport_AppendInittab("rps", &PyInit_rps);
    Py_SetProgramName(argv[0]);
    Py_Initialize();
    pName = PyUnicode_FromString("multiply");
    /* Error checking of pName left out */

    PyImport_ImportModule("rps");
    pModule = PyImport_Import(pName);
    Py_DECREF(pName);
    
    if (pModule != NULL) {
        pFunc = PyObject_GetAttrString(pModule, argv[2]);
        /* pFunc is a new reference */
        if (pFunc && PyCallable_Check(pFunc)) {
            pValue = PyObject_CallObject(pFunc, 0);
            Py_DECREF(pArgs);
            if (pValue != NULL) {
                printf("Result of call: %ld\n", PyLong_AsLong(pValue));
                Py_DECREF(pValue);
            }
            else {
                Py_DECREF(pFunc);
                Py_DECREF(pModule);
                PyErr_Print();
                fprintf(stderr,"Call failed\n");
                return 1;
            }
        }
        else {
            if (PyErr_Occurred())
                PyErr_Print();
            fprintf(stderr, "Cannot find function \"%s\"\n", argv[2]);
        }
        Py_XDECREF(pFunc);
        Py_DECREF(pModule);
    }
    else {
        PyErr_Print();
        fprintf(stderr, "Failed to load \"%s\"\n", argv[1]);
        return 1;
    }
    Py_Finalize();
    return 0;
}
