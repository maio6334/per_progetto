# to mantain shared constants

TESTING=False


MAX_COMM_ERR=3 # max communication fault in a row 

# socket constants
TCP_IP = '127.0.0.1' #  'lab00'
TCP_PORT = 23232
BUFFER_SIZE = 1024

#timeit parameter
TIMING_ITERATIONS=1 #1_000 

# constants usend to send/receive
PACKING_FORMAT='>I' 
BYTES_IN_INTEGER=4

# LDPC parameters to get a 8bit codeword
LDPC_N=21
LDPC_D_V=2
LDPC_D_C=3

# defaults and limits
DEF_MSG= '"A€𝄞.©"' #My mama always said: "Life was like a box of chocolates; you never know what you’re gonna get."'
DEF_LOG= 'log.csv'
DEF_ERR_RATE= 0.001 
MIN_ERR_RATE= 0.001
MAX_ERR_RATE= 0.1

DEF_STEPS= 30
MAX_STEPS= 500