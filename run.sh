# shell script for running convert_ND2 and get_diffusion

python convert_ND2_to_TIF --file sample_SPT.nd2

python get_diffusion.py --file sample_traj_crop.csv 
 
python get_diffusion.py --file sample_traj.csv # NOTE this one will take awhile
