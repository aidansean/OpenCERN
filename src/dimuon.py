import math

##########################################################################################
# CERN physicists use a package called ROOT.                                             #
# ROOT is free, open source, and developed "in house".                                   #
# ROOT is not perfect, but it allows you to develop quickly and (with a little           #
# practice) easily for very rapid analysis.                                              #
# See ROOT.cern.ch for more information.                                                 #
##########################################################################################
import ROOT

# Set to batch mode to prevent the splash screen and canvas windows from popping up
ROOT.gROOT.SetBatch(ROOT.kTRUE)

# Set ROOT styles to make everything look nice
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)
ROOT.gStyle.SetFillStyle(ROOT.kWhite)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetFrameBorderMode(ROOT.kWhite)
ROOT.gStyle.SetFrameFillColor(ROOT.kWhite)
ROOT.gStyle.SetCanvasBorderMode(ROOT.kWhite)
ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
ROOT.gStyle.SetPadBorderMode(ROOT.kWhite)
ROOT.gStyle.SetPadColor(ROOT.kWhite)
ROOT.gStyle.SetStatColor(ROOT.kWhite)
ROOT.gStyle.SetErrorX(0)

##########################################################################################
# General settings                                                                       #
##########################################################################################
data_prefix = '../data/'
plot_prefix = '../plots/'
filename = 'histograms.root'

# Style histograms
SS_color = ROOT.kAzure+6
#SS_color = ROOT.kViolet-1

##########################################################################################
# Classes to contain muon candidates and dimuon candidates                               #
##########################################################################################

class muon_object:
    def __init__(self, E, px, py, pz, charge):
        # Set the mother to None by default
        self.mother = None
        
        # Create the four vector using ROOT's TLorentzVector class
        self.p4 = ROOT.TLorentzVector(float(px), float(py), float(pz), float(E))
        
        # Set the charge
        self.charge = int(charge)

class dimuon_object:
    def __init__(self, mu1, mu2):
        # Save the daughters so we can reach them later
        self.mu1 = mu1
        self.mu2 = mu2
        
        # Calculate the four vector to save time later
        # ROOT's TLorentzVector class supports addition of four vectors
        self.p4 = self.mu1.p4 + self.mu2.p4
        
        # Set the charge and a flag to tell us if this is an opposite sign (OS) system
        self.charge = mu1.charge + mu2.charge
        self.isOS = True if self.charge==0 else False
        
        mu1.mother = self
        mu2.mother = self

class resonance_label:
    def __init__(self, mass, name, color):
        self.mass  = mass
        self.color = color
        self.name  = name
        self.textSize = 0.025
        
    def Draw(self, histogram):
        bin = histogram.GetXaxis().FindBin(self.mass)
        entries = histogram.GetBinContent(bin)
        width   = histogram.GetBinWidth(bin)
        
        self.line = ROOT.TLine(self.mass, 0, self.mass, entries)
        self.line.SetLineColor(self.color)
        self.line.SetLineWidth(2)
        
        self.text = ROOT.TLatex(self.mass+4*width, entries, '%s (m=%.1f GeV)'%(self.name,self.mass))
        self.text.SetTextColor(self.color)
        self.text.SetTextSize(0.03)
    
        self.line.Draw()
        self.text.Draw()

##########################################################################################
# Make some histograms                                                                   #
##########################################################################################
class binning_object:
    def __init__(self, nBins, lower, upper):
        self.nBins = nBins
        self.lower = lower
        self.upper = upper

ranges = ['full','psi','Ups']
binnings = {}
binnings['full'] = binning_object(120,0.0,120.0)
binnings['Ups' ] = binning_object(100,8.5, 12.5)
binnings['psi' ] = binning_object(100,2.0,  6.0)

hBase_mm = {}
h_mm_SS   = {}
h_mm_OSSS = {}
for rname in ranges:
    bins = binnings[rname]
    perBin = (bins.upper-bins.lower)/bins.nBins
    hBase_mm[rname] = ROOT.TH1I('hBase_mm_%s'%rname, '', bins.nBins, bins.lower, bins.upper)
    hBase_mm[rname].GetXaxis().SetTitle('m(#mu#mu) [GeV]')
    hBase_mm[rname].GetYaxis().SetTitle('entries per %.2f GeV'%perBin)

hBase_pt = ROOT.TH1I('hBase_pt','',100,0,100)
hBase_pt.GetXaxis().SetTitle('p_{T}(#mu) [GeV]')
hBase_pt.GetYaxis().SetTitle('muons per GeV')

h_pt_pos = None
h_pt_neg = None

##########################################################################################
# Load the data from file                                                                #
##########################################################################################
tfile = ROOT.TFile.Open(filename,'READ')
if tfile:
    # If the file already exists just read from it, don't bother running over events again
    for rname in ranges:
        h_mm_SS[rname]   = tfile.Get('h_mm_SS_%s'  %rname)
        h_mm_OSSS[rname] = tfile.Get('h_mm_OSSS_%s'%rname)
        
    h_pt_pos = tfile.Get('h_pt_pos')
    h_pt_neg = tfile.Get('h_pt_neg')
        
else:
    # Otherwise create the histograms and save them to file
    for rname in ranges:
        h_mm_SS[rname]   = hBase_mm[rname].Clone('h_mm_SS_%s'  %rname)
        h_mm_OSSS[rname] = hBase_mm[rname].Clone('h_mm_OSSS_%s'%rname)
    h_pt_pos = hBase_pt.Clone('h_pt_pos')
    h_pt_neg = hBase_pt.Clone('h_pt_neg')
    
    file = open('%sMuRun2010B.csv'%data_prefix)
    first_line = file.readline()
    dimuons = []
    for line in file.readlines():
        values = line.split(',')
        mu1 = muon_object(values[3] ,values[4] ,values[5] ,values[6] ,values[10])
        mu2 = muon_object(values[12],values[13],values[14],values[15],values[19])
        mumu = dimuon_object(mu1,mu2)
        M = mumu.p4.M()
        for rname in ranges:
            if mumu.charge > 0:
                h_mm_SS[rname].Fill(M)
            h_mm_OSSS[rname].Fill(M)
        #dimuons.append(mumu)
        if mu1.charge < 0:
            h_pt_neg.Fill(mu1.p4.Pt())
        else:
            h_pt_pos.Fill(mu1.p4.Pt())
        if mu2.charge < 0:
            h_pt_neg.Fill(mu2.p4.Pt())
        else:
            h_pt_pos.Fill(mu2.p4.Pt())
    
    tfile = ROOT.TFile(filename,'RECREATE')
    tfile.cd()
    for rname in ranges:
        h_mm_OSSS[rname].Write()
        h_mm_SS[rname]  .Write()
    h_pt_pos.Write()
    h_pt_neg.Write()

##########################################################################################
# Draw everything to canvas                                                              #
##########################################################################################
for rname in ranges:
    h_mm_OSSS[rname].SetMarkerStyle(20)
    h_mm_OSSS[rname].SetMarkerColor(ROOT.kBlack)
    h_mm_OSSS[rname].SetLineColor(ROOT.kBlack)

    h_mm_SS[rname].SetMarkerStyle(21)
    h_mm_SS[rname].SetMarkerColor(SS_color)
    h_mm_SS[rname].SetLineColor(SS_color)
    h_mm_SS[rname].SetFillColor(SS_color)

# Create the canvas
canvas = ROOT.TCanvas('canvas', '', 0, 0, 800, 600)
canvas.SetLogy()
canvas.SetGridx()
canvas.SetGridy()

##########################################################################################
# Create and fill legend                                                                 #
##########################################################################################
x1 = 0.15
x2 = x1+0.44
y1 = 0.90
y2 = y1-0.15
legend = ROOT.TLegend(x1,y1,x2,y2)
legend.SetBorderSize(0)

legend.AddEntry(h_mm_OSSS['full'], '#mu#mu data (all events)'      , 'pl')
legend.AddEntry(  h_mm_SS['full'], '#mu#mu data (same sign events)', 'f' )

##########################################################################################
# Create labels                                                                          #
##########################################################################################
# Create a fancy label
main_label = ROOT.TLatex(0.88, 0.94, 'CERN #font[12]{OpenData}: CMS data')
main_label.SetNDC()
main_label.SetTextAlign(32)

# Create a label for the lumi and CM energy
lumi_label = ROOT.TLatex(0.86, 0.81, '#int L dt ~ 36 pb^{-1}')
lumi_label.SetNDC()
lumi_label.SetTextAlign(31)

# Create a label for the lumi and CM energy
energy_label = ROOT.TLatex(0.87, 0.75, '#sqrt{s}=7 TeV')
energy_label.SetNDC()
energy_label.SetTextAlign(31)

# Create a label for the beams and year
beam_label = ROOT.TLatex(0.10, 0.94, '2010 pp collisions')
beam_label.SetNDC()
beam_label.SetTextAlign(12)

##########################################################################################
# Create resonance labels                                                                #
##########################################################################################
JPsi_label = resonance_label( 3.097, 'J/#psi'   , ROOT.kRed-1    )
psip_label = resonance_label( 3.686, '#psi(2S)' , ROOT.kMagenta-1)
Y1S_label  = resonance_label( 9.46 , 'Y(1S)'    , ROOT.kGreen-1  )
Y2S_label  = resonance_label(10.02 , 'Y(2S)'    , ROOT.kGreen-1  )
Y3S_label  = resonance_label(10.36 , 'Y(3S)'    , ROOT.kGreen-1  )
Z_label    = resonance_label(91.2  , 'Z'        , ROOT.kMagenta-1)

##########################################################################################
# Draw everything                                                                        #
##########################################################################################
for rname in ranges:
    canvas.Clear()
    
    minimum = 1 if h_mm_SS[rname].GetMinimum() < 1 else h_mm_SS[rname].GetMinimum()
    h_mm_OSSS[rname].SetMinimum(minimum)
    
    if rname == 'full':
        height = math.log(h_mm_OSSS[rname].GetMaximum()/h_mm_OSSS[rname].GetMinimum())/math.log(10.0)
        h_mm_OSSS[rname].SetMaximum( h_mm_OSSS[rname].GetMaximum()*math.pow(10, 0.2*height) )
    
    h_mm_OSSS[rname].SetMaximum(5*h_mm_OSSS[rname].GetMaximum())
    h_mm_OSSS[rname].Draw('pe')
    h_mm_SS[rname].Draw('sames')
    h_mm_OSSS[rname].Draw('same:pe')
    h_mm_OSSS[rname].Draw('sames:axis') # Draw axis again to overwrite line left by h_mm_SS

    h = h_mm_OSSS[rname]
    JPsi_label.Draw(h)
    Y1S_label .Draw(h)
    if rname!='full':
        psip_label.Draw(h)
        Y2S_label .Draw(h)
        Y3S_label .Draw(h)
    Z_label   .Draw(h)

    legend.Draw()
    main_label.Draw()
    lumi_label.Draw()
    beam_label.Draw()
    energy_label.Draw()

    canvas.Print('%smumu_spectrum_%s.pdf'%(plot_prefix, rname))
    canvas.Print('%smumu_spectrum_%s.png'%(plot_prefix, rname))

h_pt_pos.SetMarkerStyle(20)
h_pt_pos.SetMarkerColor(ROOT.kBlack)
h_pt_pos.SetLineColor(ROOT.kBlack)

h_pt_neg.SetMarkerStyle(21)
h_pt_neg.SetMarkerColor(SS_color)
h_pt_neg.SetLineColor(SS_color)
h_pt_neg.SetFillColor(SS_color)

h_pt_pos.Draw('pe')
h_pt_neg.Draw('sames')
h_pt_pos.Draw('sames:pe')
h_pt_pos.Draw('same:axis')
canvas.Print('%smumu_pt.pdf'%plot_prefix)
canvas.Print('%smumu_pt.png'%plot_prefix)

canvas.SetLogy(False)
h_pt_diff = h_pt_pos.Clone('h_pt_diff')
h_pt_diff.Sumw2()
for bin in range(1, h_pt_diff.GetNbinsX()+1):
    value = h_pt_pos.GetBinContent(bin)-h_pt_neg.GetBinContent(bin)
    error = math.sqrt(h_pt_pos.GetBinContent(bin)+h_pt_neg.GetBinContent(bin))
    h_pt_diff.SetBinContent(bin, value)
    h_pt_diff.SetBinError  (bin, error)
h_pt_diff.Draw('pe')
canvas.Print('%smumu_pt_diff.pdf'%plot_prefix)
canvas.Print('%smumu_pt_diff.png'%plot_prefix)
