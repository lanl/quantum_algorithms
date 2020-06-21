args           = readcsv("arguments.csv")

file_data      = strip(args[1])
gradient_step  = args[2]
num_iter       = args[3]
data           = eval.(parse.(readcsv(file_data,String)))


(measures, dimension)   = size(data)
dimension               = dimension - 1

density_matrix = eye(Complex{Float64},dimension)


for t = 1:num_iter
    gradient = zeros(Complex{Float64},dimension,dimension)
    for k=1:measures
        weight      = data[k,1]
        proj_vect   = data[k,2:dimension + 1] / norm(data[k,2:dimension + 1])
        denominator = *(proj_vect',*(density_matrix, proj_vect))

        if real(denominator) >= (10.0)^(-6.0)
            partial_grad = *(proj_vect, proj_vect')
            gradient = gradient - partial_grad * (weight/denominator)
        end
    end

    density_matrix = density_matrix - gradient_step * gradient
    eigdec = eigfact(density_matrix)
    index_list = sortperm(real.(eigdec.values), rev=true)
    index_set  = [index_list[1]]
    mu = real(eigdec.values[index_list[1]])

    for i=2:dimension
        lambda = real(eigdec.values[index_list[i]])

        if i*lambda  >= (mu + lambda - 1.0)
            mu   = mu + lambda
            push!(index_set, index_list[i])
        else
            break
        end
    end
    mu = (mu - 1.0) / length(index_set)

    density_matrix = zeros(Complex{Float64},dimension,dimension)
    for i=1:length(index_set)
        weight          = eigdec.values[index_set[i]] - mu
        eigen_vect      = eigdec.vectors[1:dimension,index_set[i]] / norm(eigdec.vectors[1:dimension,index_set[i]])
        density_matrix  = density_matrix + weight* *(eigen_vect,eigen_vect')
    end
end
writecsv("density_matrix.csv", density_matrix)
dm_eigdec = eigfact(density_matrix)
writecsv("eig_values.csv", dm_eigdec.values)
writecsv("eig_vectors.csv", dm_eigdec.vectors)
println(density_matrix)