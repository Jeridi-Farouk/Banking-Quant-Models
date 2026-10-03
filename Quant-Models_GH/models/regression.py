import numpy as np

a=[[3,4,5],[2,3,4],[3,6,1]]
b=[[7,16,14]]
def regression(a,b):

    a=np.array(a)
    b=np.array(b).reshape(-1,1)

    if a.shape[0] != b.shape[0]:

        print("Error: the matrix and the array must be the same number of rows")
        return

    ones=np.ones((a.shape[0],1))
    x=np.hstack([ones,a])

   

    xtx=x.T@x
    xtb=x.T@b

    beta=np.linalg.solve(xtx,xtb)
    print(x)
    print(b)
    print(xtb)
    print(xtx)
    print(beta)

regression(a,b)


