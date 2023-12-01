from itertools import product
filename="gemm"
# Define the permutations for each line
m_values = ['set_directive_resource -core RAM_1P_BRAM', 'set_directive_array_partition -factor 64 -type cyclic']
l_values = ['set_directive_unroll -factor 8', 'set_directive_pipeline']
var=["m1","m2","prod"]
loop=["inner","middle","outer"]
# Generate permutations
permutations_m = list(product(m_values, repeat=3))
permutations_l = list(product(l_values, repeat=3))

# Generate files with permutations
total_permutations = min(len(permutations_m), len(permutations_l))
for i in range(total_permutations):
    with open(f'gemm_dir_{i}', 'w') as file:
        for j in range(3):
            file.write(f'{permutations_m[i][j]} {filename} {var[j]}\n')
            file.write(f'{permutations_l[i][j]} {filename}/{loop[j]}\n')
        file.write('\n')
    print("combination",i)
