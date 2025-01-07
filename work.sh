workdir='xxx'
bin='xxx'
input='INS.fasta'

# repeatmask
[ -d repeatmask ] || mkdir repeatmask
RepeatMasker -pa 24  -s -species human -e ncbi -dir repeatmask -gff INS.fasta
cd repeatmask
sed -n '4,$p' INS.fasta.out |awk '{print $5"\t"$6-1"\t"$7"\t"$11}' > INS.fasta.repeatmask.bed
python3 $bin/reclass.repeat.py $bin/reclass.template.tsv INS.fasta.repeatmask.bed > INS.fasta.repeatmask.reclass.bed
cd ..

# etr
$bin/etrf/etrf INS.fasta > INS.etrf.out
awk '$5>=7' INS.etrf.out |awk '{print $1"\t"$2"\t"$3"\tVNTR"}'> ins.VNTR.bed
awk '$5<=6' INS.etrf.out | awk '{print $1"\t"$2"\t"$3"\tSTR"}' > ins.STR.bed

# aSat
$bin/dna-nn/dna-brnn -Ai  $bin/dna-nn/models/attcc-alpha.knm -t16 INS.fasta > ins.seq.aSat.bed
awk '$4==2' ins.seq.aSat.bed|awk '{print $1"\t"$2"\t"$3"\tother_repeat"}'  > ins.aSat.bed

# sd
minimap2 -cxasm20 -r2k --cs  -t 24 ${reference_sd.fasta} INS.fasta > ins.map2ref.paf
cat ins.map2ref.paf|awk '{print $1"\t"$2"\t"$3"\t"$4"\t"($4-$3)/$2"\t"$6"\t"$7"\t"$8"\t"$9"\t"($9-$8)/$7"\t"$10/$11}'  > ins.map2ref.sd.info
awk '$4-$3>=1000 && $5>=0.2' ins.map2ref.sd.info > ins.map2ref.sd.info.filt
cut -f 1,3,4 ins.map2ref.sd.info.filt|sort -k1,1V -k2n | uniq |sort -k1,1V -k2n| bedtools merge -i - | awk '{print $0"\tSD"}'> ins.sd.bed


# summary
cat repeatmask/INS.fasta.repeatmask.reclass.bed ins.VNTR.bed ins.STR.bed ins.aSat.bed ins.sd.bed | sort -k1,1V -k2,2n  > ins.combined.anno.bed
bedtools intersect -a ins.bed -b ins.combined.anno.bed -wo |awk '{print $0"\t"$8/($3-$2)}' |sort  -k1,1V -k2,5n > ins.combined.anno.bed.info
python3  $bin/merge_adjacent_annot.py ins.combined.anno.bed.info > ins.combined.anno.merged.filt.bed
