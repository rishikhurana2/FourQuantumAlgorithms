from qiskit.quantum_info.operators import Operator
from qiskit import *
from qiskit.visualization import plot_histogram
from qiskit.circuit import Gate
import numpy as np
from qiskit.providers.fake_provider import FakeManilaV2
import math

def Grover(func_oracle, n, noise=False):
  qc = QuantumCircuit(n, n)
  qc.reset(range(n))

  qc.barrier()

  #prepare the qubits (apply Hadamard to each one)
  qc.h([i for i in range(n)])

  qc.barrier()
  #Grover's Loop

  #consutrct Z_0 as a unitary matrix
  Z_0 = QuantumCircuit(n, name = "Z_0")
  matrix = np.zeros((2**n,2**n)) #requries 2**(2n) entries because applying matrix to n qubits -- meaning there are 2**n entries for each input
  for i in range(2**n):
    for j in range(2**n):
      if (i == 0 and j == 0):
        matrix[i][j] = -1 #Z_0 has unitary matrix [[-1, 0, 0, 0, ...], [0,1, 0, ...], [0,0,1, ...], ...] because Z_0|0^n> = -|0^n> and Z_0|x> = |x> forall x not equal to 0^n
      elif (i == j):
        matrix[i][j] = 1
  Z_0.unitary(matrix, [i for i in range(n)]) #Implementing Z_0 as a gate representing the unitary matrix computed above
  sub_Z_0_circ = Z_0.to_instruction()

  #Construct Z_f
  sub_Z_f_circ = func_oracle.to_instruction() #black-boxed function oracle

  #Apply grover's loop O(sqrt(2**n)) times
  k = round(((math.pi)/4)*math.sqrt(2**n) - 1/2) #computing the iterations necessary for optimal rotation to measure |A>
  for i in range(k):
    #Applying G = H^{xn} * Z_0 * H^{xn} * Z_f
    qc.append(sub_Z_f_circ, [i for i in range(n)]) #appending function oracle to circuit
    qc.h([i for i in range(n)]) 
    qc.append(sub_Z_0_circ, [i for i in range(n)]) #appendding Z_0 to circuit
    qc.h([i for i in range(n)])

  qc.barrier()

  qc.measure([i for i in range(n)], [i for i in range(n)]) #measure the final result -- outputting x such that f(x) = 1 with high probability

  #code below is for output using simulator
  if (not(noise)):
    backend = Aer.get_backend("aer_simulator") #accurate simualtor using no noise
  else:
    backend = FakeManilaV2() #fake noise simnulator to prevent running on actual quantum computer (high queue times) if noise option is chosen
  job = backend.run(qc.decompose(), shots=1, memory=True)
  output = job.result().get_memory()[0][::-1] #needs to be reversed because stored in little endian format

  return qc, output