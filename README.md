#### Run in background
```
nohup python3 START.py &
```

#### Bring back to foreground
```
ps ax | grep START.py
```

#### Start with
```
python3.6 -m tradeogrebot.START
```

#### For installation of `orca`
```
https://github.com/plotly/orca
```

#### Install `orca` with
```
sudo npm install -g electron@1.8.4 orca
```
or with [Conda](https://conda.io/miniconda.html)
```
conda install -c plotly plotly-orca psutil
```

#### First make sure to have installed
```
sudo apt-get install python3.6-dev
```

#### Make sure to have this installed also
```
apt-get install libgconf-2-4
```

#### If error `xvfb-run: error:Xvfb failed to start` 
```
xvfb-run -a /path/to/orca "$@"
```