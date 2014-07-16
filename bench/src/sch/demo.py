"""
Demonstrate 3D seismic image processing for faults and horizons
Author: Dave Hale, Colorado School of Mines
Version: 2014.06.17
"""

from schutils import *
setupForSubset("s2a")
s1,s2,s3 = getSamplings()
n1,n2,n3 = s1.count,s2.count,s3.count

# Names and descriptions of image files used below.
g0file  = "g0" # raw input image
gxfile  = "gx" # input image, after bilateral filtering
gsxfile = "gsx" # image after lsf with sharp faults
gwfile  = "gw" # image after unfaulting
epfile  = "ep" # eigenvalue-derived planarity
p2file  = "p2" # inline slopes
p3file  = "p3" # crossline slopes
flfile  = "fl" # fault likelihood
fpfile  = "fp" # fault strike (phi)
ftfile  = "ft" # fault dip (theta)
fltfile = "flt" # fault likelihood thinned
fptfile = "fpt" # fault strike thinned
fttfile = "ftt" # fault dip thinned
fs1file = "fs1" # fault slip (1st component)
fs2file = "fs2" # fault slip (2nd component)
fs3file = "fs3" # fault slip (3rd component)

# Processing begins here. When experimenting with one part of this demo, we
# can disable other parts that have already written results to files.
displayOnly = False
scanName = ""
def main(args):
  #goDisplay()
  #goSlopes()
  #for scanName in ["000"]:
  #  goScan()
  #  goThin()
  #  goSmooth()
  #  goSkin()
  #  goSlip()
  #goUnfault()

def goDisplay():
  print "goDisplay ..."
  g0 = readImage(g0file)
  gx = readImage(gxfile)
  plot3(g0)
  plot3(gx)

def goSlopes():
  print "goSlopes ..."
  gx = readImage(gxfile)
  if not displayOnly:
    sigma1,sigma2,sigma3,pmax = 16.0,2.0,2.0,2.0
    p2,p3,ep = FaultScanner.slopes(sigma1,sigma2,sigma3,pmax,gx)
    writeImage(p2file,p2)
    writeImage(p3file,p3)
    writeImage(epfile,ep)
  else:
    p2 = readImage(p2file)
    p3 = readImage(p3file)
    ep = readImage(epfile)
  print "p2 min =",min(p2)," max =",max(p2)
  print "p3 min =",min(p3)," max =",max(p3)
  print "ep min =",min(ep)," max =",max(ep)
  plot3(gx,p2,cmin=-1.0,cmax=1.0,cmap=bwrNotch(1.0))
  plot3(gx,p3,cmin=-1.0,cmax=1.0,cmap=bwrNotch(1.0))
  plot3(gx,sub(1,ep),cmin=0,cmax=0.5,cmap=jetRamp(1.0))

def goScan():
  print "goScan ..."
  p2 = readImage(p2file)
  p3 = readImage(p3file)
  gx = readImage(gxfile)
  if not displayOnly:
    gtx = FaultScanner.taper(50,0,0,gx);
    #sigmaPhi,sigmaTheta = 4,20 # typical values
    sigmaPhi,sigmaTheta = 8,40 # because sampling intervals are small
    minPhi,maxPhi = 0,360
    minTheta,maxTheta = 65,85
    fsc = FaultScanner(sigmaPhi,sigmaTheta)
    fl,fp,ft = fsc.scan(minPhi,maxPhi,minTheta,maxTheta,p2,p3,gtx)
    writeImage(flfile,fl)
    writeImage(fpfile,fp)
    writeImage(ftfile,ft)
  else:
    fl = readImage(flfile)
    fp = readImage(fpfile)
    ft = readImage(ftfile)
  print "fl min =",min(fl)," max =",max(fl)
  print "fp min =",min(fp)," max =",max(fp)
  print "ft min =",min(ft)," max =",max(ft)
  plot3(gx,fl,cmin=0.1,cmax=1,cmap=jetRamp(1.0))
  plot3(gx,fp,cmin=0,cmax=360,cmap=hueFill(0.3))
  plot3(gx,ft,cmin=60,cmax=90,cmap=jetFill(0.3))

def goThin():
  print "goThin ..."
  gx = readImage(gxfile)
  if not displayOnly:
    fl = readImage(flfile)
    fp = readImage(fpfile)
    ft = readImage(ftfile)
    flt,fpt,ftt = FaultScanner.thin([fl,fp,ft])
    writeImage(fltfile,flt)
    writeImage(fptfile,fpt)
    writeImage(fttfile,ftt)
  else:
    flt = readImage(fltfile)
    fpt = readImage(fptfile)
    ftt = readImage(fttfile)
  plot3(gx,flt,cmin=0.1,cmax=1.0,cmap=jetFillExceptMin(1.0))
  plot3(gx,fpt,cmin=-1.5,cmax=360,cmap=hueFillExceptMin(1.0))
  plot3(gx,ftt,cmin=60,cmax=90,cmap=jetFillExceptMin(1.0))

def goSmooth():
  print "goSmooth ..."
  gx = readImage(gxfile)
  if not displayOnly:
    flstop = 0.1
    fsigma = 8.0
    gx = readImage(gxfile)
    flt = readImage(fltfile)
    p2 = readImage(p2file)
    p3 = readImage(p3file)
    gsx = FaultScanner.smooth(flstop,fsigma,p2,p3,flt,gx)
    writeImage(gsxfile,gsx)
  else:
    gsx = readImage(gsxfile)
  plot3(gx)
  plot3(gsx)

def goSkin():
  print "goSkin ..."
  gx = readImage(gxfile)
  gsx = readImage(gsxfile)
  if not displayOnly:
    p2 = readImage(p2file)
    p3 = readImage(p3file)
    fl = readImage(flfile)
    fp = readImage(fpfile)
    ft = readImage(ftfile)
    fs = FaultSkinner([fl,fp,ft])
    fs.setGrowLikelihoods(0.1,0.5)
    fs.setMinSkinSize(40000)
    cells = fs.findCells()
    skins = fs.findSkins(cells)
    for skin in skins:
      skin.smoothCellNormals(4)
    print "total number of cells =",len(cells)
    print "total number of skins =",len(skins)
    removeAllSkinFiles("skin")
    writeSkins("skin",skins)
    plot3(gx,cells=cells)
  else:
    skins = readSkins("skin")
  plot3(gx,skins=skins)
  #for skin in skins:
  #  plot3(gx,skins=[skin],links=True)

def goSlip():
  print "goSlip ..."
  gx = readImage(gxfile)
  skins = readSkins("skin")
  if not displayOnly:
    gsx = readImage(gsxfile)
    p2 = readImage(p2file)
    p3 = readImage(p3file)
    fs = FaultSlipper(gsx,p2,p3)
    fs.setZeroSlope(False)
    fs.computeDipSlips(skins,0.0,20.0)
    smark = -1000.0
    s1,s2,s3 = fs.getDipSlips(skins,smark)
    s1,s2,s3 = fs.interpolateDipSlips([s1,s2,s3],smark)
    writeImage(fs1file,s1)
    writeImage(fs2file,s2)
    writeImage(fs3file,s3)
  else:
    s1 = readImage(fs1file)
  plot3(gx,skins=skins,smax=20.0)
  plot3(gx,s1,cmin=0.0,cmax=20.0,cmap=jetFill(0.3))

def goUnfault():
  print "goUnfault ..."
  gx = readImage(gxfile)
  if not displayOnly:
    s1 = readImage(fs1file)
    s2 = readImage(fs2file)
    s3 = readImage(fs3file)
    gw = FaultSlipper.unfault([s1,s2,s3],gx)
    writeImage(gwfile,gw)
  else:
    gw = readImage(gwfile)
  plot3(gw)
  plot3(gx)

#############################################################################
# graphics

def jetFill(alpha):
  return ColorMap.setAlpha(ColorMap.JET,alpha)
def jetFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.JET,a)
def jetRamp(alpha):
  return ColorMap.setAlpha(ColorMap.JET,rampfloat(0.0,alpha/256,256))
def bwrFill(alpha):
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,alpha)
def bwrNotch(alpha):
  a = zerofloat(256)
  for i in range(len(a)):
    if i<128:
      a[i] = alpha*(128.0-i)/128.0
    else:
      a[i] = alpha*(i-127.0)/128.0
  return ColorMap.setAlpha(ColorMap.BLUE_WHITE_RED,a)
def hueFill(alpha):
  return ColorMap.getHue(0.0,1.0,alpha)
def hueFillExceptMin(alpha):
  a = fillfloat(alpha,256)
  a[0] = 0.0
  return ColorMap.setAlpha(ColorMap.getHue(0.0,1.0),a)

def plot3(f,g=None,cmin=None,cmax=None,cmap=None,
          xyz=None,cells=None,skins=None,smax=0.0,
          links=False,curve=False,trace=False):
  n1 = len(f[0][0])
  n2 = len(f[0])
  n3 = len(f)
  sf = SimpleFrame(AxesOrientation.XRIGHT_YOUT_ZDOWN)
  if g==None:
    ipg = sf.addImagePanels(s1,s2,s3,f)
    if cmap!=None:
      ipg.setColorModel(cmap)
    if cmin!=None and cmax!=None:
      ipg.setClips(cmin,cmax)
    else:
      ipg.setClips(-1.0,1.0)
  else:
    ipg = ImagePanelGroup2(s1,s2,s3,f,g)
    ipg.setClips1(-1.0,1.0)
    if cmin!=None and cmax!=None:
      ipg.setClips2(cmin,cmax)
    if cmap==None:
      cmap = jetFill(0.8)
    ipg.setColorModel2(cmap)
    sf.world.addChild(ipg)
  if xyz:
    pg = PointGroup(0.2,xyz)
    ss = StateSet()
    cs = ColorState()
    cs.setColor(Color.YELLOW)
    ss.add(cs)
    pg.setStates(ss)
    #ss = StateSet()
    #ps = PointState()
    #ps.setSize(5.0)
    #ss.add(ps)
    #pg.setStates(ss)
    sf.world.addChild(pg)
  if cells:
    ss = StateSet()
    lms = LightModelState()
    lms.setTwoSide(True)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    cmap = ColorMap(0.0,1.0,ColorMap.JET)
    xyz,uvw,rgb = FaultCell.getXyzUvwRgbForLikelihood(0.5,cmap,cells)
    qg = QuadGroup(xyz,uvw,rgb)
    qg.setStates(ss)
    sf.world.addChild(qg)
  if skins:
    sg = Group()
    ss = StateSet()
    lms = LightModelState()
    lms.setTwoSide(True)
    ss.add(lms)
    ms = MaterialState()
    ms.setSpecular(Color.GRAY)
    ms.setShininess(100.0)
    ms.setColorMaterial(GL_AMBIENT_AND_DIFFUSE)
    if not smax:
      ms.setEmissiveBack(Color(0.0,0.0,0.5))
    ss.add(ms)
    sg.setStates(ss)
    size = 2.0
    if links:
      size = 0.5 
    for skin in skins:
      if smax>0.0: # show fault throws
        cmap = ColorMap(0.0,smax,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForThrow(size,cmap)
      else: # show fault likelihood
        cmap = ColorMap(0.0,1.0,ColorMap.JET)
        xyz,uvw,rgb = skin.getCellXyzUvwRgbForLikelihood(size,cmap)
      qg = QuadGroup(xyz,uvw,rgb)
      qg.setStates(None)
      sg.addChild(qg)
      if curve or trace:
        cell = skin.getCellNearestCentroid()
        if curve:
          xyz = cell.getFaultCurveXyz()
          pg = PointGroup(0.5,xyz)
          sg.addChild(pg)
        if trace:
          xyz = cell.getFaultTraceXyz()
          pg = PointGroup(0.5,xyz)
          sg.addChild(pg)
      if links:
        xyz = skin.getCellLinksXyz()
        lg = LineGroup(xyz)
        sg.addChild(lg)
    sf.world.addChild(sg)
  #ipg.setSlices(95,21,51)
  #ipg.setSlices(95,5,95)
  sf.setSize(1400,900)
  vc = sf.getViewCanvas()
  vc.setBackground(Color.WHITE)
  ov = sf.getOrbitView()
  #ov.setAxesScale(1.0,1.0,4.0)
  ov.setScale(2.5)
  #radius = 0.5*sqrt(n1*n1+n2*n2+n3*n3)
  #ov.setWorldSphere(BoundingSphere(0.5*n1,0.5*n2,0.5*n3,radius))
  #ov.setAzimuthAndElevation(-55.0,25.0)
  #ov.setTranslate(Vector3(0.0241,0.0517,0.0103))

#############################################################################
run(main)