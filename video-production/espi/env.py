import sys,subprocess,numpy as np
src=sys.argv[1]
for t in map(float,sys.argv[2:]):
    a=t-1.0; x=np.frombuffer(subprocess.check_output(["ffmpeg","-v","error","-ss",str(a),"-i",src,"-t","2","-ac","1","-ar","16000","-f","f32le","-"]),np.float32)
    r=[20*np.log10(np.sqrt(np.mean(x[i:i+1600]**2))+1e-9) for i in range(0,len(x)-1599,1600)]
    print(f"{t:7.1f}: "+" ".join(f"{a+i*0.1:.1f}:{v:.0f}" for i,v in enumerate(r)))
