open_project gemm_hls

add_files gemm.c
add_files input.data
add_files check.data
add_files -tb ../../common/harness.c
#add_files -tb gemm_test.c

set_top gemm


for {set i 0} {$i < 8} {incr i} {
	open_solution "solution$i"
	set_part virtex7
	create_clock -period 10
	source "./gemm_dir_$i"
	csynth_design

}


exit
