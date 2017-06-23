import pandas as pd
import ort

class block:
	def __init__(self,pp_id,exp_type,vmrk,log,bid):
		self.pp_id = pp_id
		self.exp_type = exp_type
		self.vmrk = vmrk
		self.log = log
		self.bid = bid
		self.set_info()
		self.load_orts()

	def __str__(self):
		m = '\nBLOCK OBJECT\n'
		m += 'marker\t\t\t'+str(self.marker) + '\n'
		m += 'wav_filename\t\t'+str(self.wav_filename) + '\n'
		m += 'fids\t\t\t'+' - '.join(self.fids) + '\n'
		m += 'sids\t\t\t'+' - '.join(self.sids) + '\n'
		m += 'start sample\t\t'+str(self.st_sample) + '\n'
		m += 'end sample\t\t'+str(self.et_sample) + '\n'
		m += 'duration sample\t\t'+str(self.duration_sample) + '\n'
		m += 'wav duration\t\t'+str(self.wav_dur) + '\n'
		m += 'sample inaccuracy\t' + str(self.sample_inacc) + '\n'
		m += 'start time\t\t'+str(self.st) + '\n'
		m += 'et time\t\t\t'+str(self.et) + '\n'
		m += 'duration\t\t'+str(self.duration) + '\n'
		return m

	def set_info(self):
		self.l = self.log.log
		self.marker = self.l[self.l['block'] == self.bid]['marker'].values[0]
		self.wav_filename = self.log.marker2wav[self.marker]
		self.fids = self.log.marker2fidlist[self.marker]
		self.sids = self.log.fid2sid[self.fids[0]] # sid does not vary in block
		self.st_sample = self.vmrk.marker2samplen[self.marker]
		self.et_sample = self.vmrk.marker2samplen[self.marker+1]
		self.duration_sample = self.et_sample - self.st_sample
		self.wav_dur= self.l[self.l['block'] == self.bid]['wav_duration'].values[0]
		self.sample_inacc = abs(self.duration_sample -self.wav_dur)
		self.st = self.l[self.l['block'] == self.bid]['start_time'].values[0]
		self.et = self.l[self.l['block'] == self.bid]['end_time'].values[0]
		self.duration = self.et - self.st
		if self.exp_type == 'ifadv': 
			self.corpus = 'IFADV'
			self.register = 'spontaneous_dialogue'
		elif self.exp_type == 'o': 
			self.corpus = 'CGN'
			self.register = 'read_aloud_stories'
		elif self.exp_type == 'k': 
			self.corpus = 'CGN'
			self.register = 'news_broadcast' 

	def load_orts(self):
		# create the ort file for all fids in the block 
		# ( a block is 1 experimental wav file which can consist of 
		# multiple wav from comp-o or comp-k (always 1 for ifadv)
		k_wav_offset_second = 0.9
		k_wav_offset_sample= 900
		self.orts = []
		self.words = []
		total_fids_offset = 0
		self.ncontent_words = 0
		for i,fid in enumerate(self.fids):
			# create ort object for fid
			self.orts.append(ort.Ort(fid,self.sids[0],corpus = self.corpus,register = self.register))
			if self.exp_type == 'ifadv':
				# add extra speaker for ifadv and check for overlap between speakers
				self.orts[-1].add_speaker(self.sids[1])
				self.orts[-1].check_overlap()
			for w in self.orts[-1].words:
				# set sample offset (when did the recording start playing 
				# in sample time, if wav consist of multiple wav add offset
				# k (news) also had an pause between files of .9 seconds
				if self.exp_type == 'k' and i > 0:
					total_fids_offset += last_fid_duration + k_wav_offset_sample
				elif self.exp_type == 'o' and i > 0:
					total_fids_offset += last_fid_duration 
				else:
					total_fids_offset = 0
				# set samplenumber for each word
				w.set_times_as_samples(offset=total_fids_offset + self.st_sample)
			if self.exp_type in ['o','k']:
				# get the duration of the las wav file
				last_fid_duration = self.log.fid2dur[fid]
			# add all words of the ort object corresponding to fid to the block
			self.words.extend(self.orts[-1].words)
		# count number of words in this block
		self.nwords = len(self.words)




			
