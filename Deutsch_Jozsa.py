from qiskit.quantum_info.operators import Operator
from qiskit import *
from qiskit.visualization import plot_histogram
from qiskit.circuit import Gate
import numpy as np
from qiskit.providers.fake_provider import FakeManilaV2
import math

def Deutsch_Jozsa(func_oracle, n, noise=False):
  qc = QuantumCircuit(n + 1, 1)
  qc.reset(range(n + 1))
  qc.x(n) #setting the helper bit to |1>

  qc.barrier()

  #prepare bits for application of func_oracle
  for i in range(0, n + 1):
    qc.h(i) #apply hadamard to all bits

  qc.barrier()

  #apply func_oracle
  U_f = func_oracle.to_instruction() #black-boxed function oracle
  qc.append(U_f, [i for i in range(n + 1)]) #appending function oracle to circuit

  qc.barrier()

  #post-process from application of func_oracle
  for i in range(0, n):
    qc.h(i) #apply hadamard to first n bits

  qc.barrier()

  #measure the first qubit
  qc.measure(0, 0)



  #code below is for output using simulator
  if (not(noise)):
    backend = Aer.get_backend("aer_simulator") #accurate simualtor using no noise
  else:
    backend = FakeManilaV2() #fake noise simnulator to prevent running on actual quantum computer (high queue times) if noise option is chosen
  job = backend.run(qc.decompose(), shots=1, memory=True)
  output = job.result().get_memory()[0] #no need to reverse b/c only 1 bit output

  return qc, output
