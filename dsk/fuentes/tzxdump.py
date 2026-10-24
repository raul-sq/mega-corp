import sys,struct
def blocks(path):
    d=open(path,'rb').read()
    assert d[:8]==b'ZXTape!\x1a', d[:8]
    p=10; out=[]
    while p<len(d):
        bid=d[p]; p+=1
        if bid==0x10:
            pause,ln=struct.unpack_from('<HH',d,p); data=d[p+4:p+4+ln]; p+=4+ln
            out.append((bid,pause,data))
        elif bid==0x11:
            ln=d[p+15]|d[p+16]<<8|d[p+17]<<16; data=d[p+18:p+18+ln]; out.append((bid,0,data)); p+=18+ln
        elif bid==0x30:
            n=d[p]; out.append((bid,0,d[p+1:p+1+n])); p+=1+n
        elif bid==0x32:
            ln=struct.unpack_from('<H',d,p)[0]; out.append((bid,0,d[p+2:p+2+ln])); p+=2+ln
        elif bid==0x20:
            out.append((bid,0,d[p:p+2])); p+=2
        else:
            raise Exception('block %x at %d'%(bid,p))
    return out
if __name__=='__main__':
    for bid,pause,data in blocks(sys.argv[1]):
        if bid in(0x10,0x11):
            flag=data[0]
            if flag==0 and len(data)==19:
                t,name,ln,p1,p2=struct.unpack_from('<B10sHHH',data,1)
                print(hex(bid),'HDR type',t,name,'len',ln,'p1',p1,'p2',p2)
            else:
                x=0
                for b in data: x^=b
                print(hex(bid),'DATA flag',flag,'len',len(data)-2,'chk ok' if x==0 else 'BAD')
        else: print(hex(bid),data[:60])
