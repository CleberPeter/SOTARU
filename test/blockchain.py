import sys
import os

def generate(number_blocks):
    
    f = open('test/blockchain.dat', 'w')
    
    for i in range(number_blocks):
        
        block = ''
        block += 'add_node\n'
        block += str(i) + '\n'
        block += 'f4f14079719f404b8556018069d3c81eebfee64f00c59b85813101eacc367a96\n'
        
        block += 'localhost\n'
        block += '5057\n'
        block += '8080\n'  
        
        block_size = len(block)
        block = str(block_size) + '\n' + block

        f.write(block)

    f.close()

def search(name):
    f = open('test/blockchain.dat', 'r')
    
    while True:
    
        size = f.readline()
        pos_i = f.tell()
        if size != '':
            typ = f.readline()
            if typ == 'add_node\n':
                name = f.readline()
                if name == '9999\n':
                    print('name: ', name)
                    print('hash: ', f.readline())
                    print('tcp_port: ', f.readline())
                    print('http_port: ', f.readline())
            pos_f = f.tell()
            f.seek(f.tell() + int(size) - (pos_f - pos_i) )
        else:
            break
    
    f.close()

if __name__ == "__main__":

    number_blocks = int(sys.argv[1])
    # generate(number_blocks)
    search("1235")
