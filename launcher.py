import os

# Menu Interface
if __name__ == '__main__':
    for f in os.listdir():
        if f.startswith('oscarbot'):
            os.system(f)
    
