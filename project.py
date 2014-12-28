from project_module import project_object, image_object, link_object, challenge_object

p = project_object('CERNOpenDataCMS', 'CERN Open Data (CMS)')
p.domain = 'http://www.aidansean.com/'
p.path = 'CERNOpenData/CMS'
p.preview_image_ = image_object('http://placekitten.com.s3.amazonaws.com/homepage-samples/408/287.jpg', 408, 287)
p.github_repo_name = 'CERNOpenDataCMS'
p.mathjax = True
p.links.append(link_object(p.domain, 'CERNOpenData/CMS', 'Live page'))
p.introduction = 'In 2014 the CMS experiment at CERN released their 2010 data to the public for analysis.  As a quick exercise I decided to analyse the dimuon mass spectrum to show that this could be done in a reasonable amount of time.'
p.overview = '''The input file is the 2010 Run B comma separated values file.  The python script then produces mass spectra for same sign and opposite sign mass spectra and zooms in on the interesting regions.'''

p.challenges.append(challenge_object('The main challenge was that this project was made as quickly as possible.', 'This project uses python and existing ROOT libraries for the maximal development speed.  The other data format available was using CMSSW and a virtual machine.  In principle using CMSSW should be straightforward, but I decided against using this because the software was already four years old and support would be minimal or non-existant, even to current CMS physicsts.', 'Resolved'))
