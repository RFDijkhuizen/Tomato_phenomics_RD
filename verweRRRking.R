#' --- 
#' title: "Verwerrrking data"
#' ---
library(rjson)
library(stringr)
library(ggplot2)
library(alphashape3d)

#' This processing script is divided in 4 parts for now. One part for each of the output
#' files.

#' # TOP PERSPECTIVE RGB IMAGE
#' This part of the codes reads the output from the top perspective RGB images. 
#' In the end I probably only want to use color from these.
setwd("~/rens2")

## get data
file.list <- list.files("output/")
file.list <- file.list[grep("cam9top_results.txt",file.list)]

## open one temp file
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
#' To simplify the complicated output I now simply take the mean, this is just a temporary solution.
pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
pheno.tmp <- NULL
for (i in 1:length(tmp$observations)){
  if (length(tmp$observations[[i]]$value) > 1){
    pheno.tmp <- c(pheno.tmp,mean(tmp$observations[[i]]$value))
  }
  else{
    pheno.tmp <- c(pheno.tmp,tmp$observations[[i]]$value)
      
  }
}
pheno.collect[j,] <- pheno.tmp
}
colnames(pheno.collect) <- trait.list
rownames(pheno.collect) <- file.list
pheno.collect[1:5,1:5]
pheno.collect <- data.frame(pheno.collect)
pheno.collect$genotype <- as.factor(pheno.collect$genotype)
pheno.collect$whether.the.plant.goes.out.of.bounds. <- as.factor(pheno.collect$whether.the.plant.goes.out.of.bounds.)
pheno.collect$object.in.frame <- as.factor(pheno.collect$object.in.frame)
#' random nice plots.
#' The plots dont really work at the moment because ~ genotype doesnt work now that the genotype
#' is a string and not a number (I think)
plot(pheno.collect$area)
ggplot(pheno.collect, aes(x = object.in.frame)) + geom_boxplot()
ggplot(pheno.collect, aes(x = genotype)) + geom_bar()
ggplot(pheno.collect[1:10,1:36], aes(y = area, x= genotype)) + geom_boxplot()
small_subset <- subset(pheno.collect, genotype == "207A" | genotype == "271A" | genotype == "278A" | genotype == "283A")
ggplot(small_subset, aes(y = area, x= genotype)) + geom_boxplot()
boxplot(pheno.collect$area ~ pheno.collect$genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect, notch = TRUE )
qplot(geom = 'boxplot',genotype, area, data = pheno.collect)


#' # TOP perspective 3D data
#' This part of the code handles the output from the 3D data from top perspective.
#' Currently mostly gives NA's.

## get data
file.list <- list.files("output/")
file.list <- file.list[grep("3D_top_results.txt",file.list)]

## open one temp file
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}

pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
  pheno.tmp <- NULL
  for (i in 1:length(tmp$observations)){
    print(length(mean(tmp$observations[[i]]$value)))
    pheno.tmp <- c(pheno.tmp,mean(tmp$observations[[i]]$value))

  }
  pheno.collect[j,] <- pheno.tmp
}
colnames(pheno.collect) <- trait.list
rownames(pheno.collect) <- file.list
pheno.collect[1:5,1:5]
pheno.collect <- data.frame(pheno.collect)

#' RANDOM NICE PLOTS
plot(pheno.collect$area.above.reference)
plot(pheno.collect$area)

boxplot(pheno.collect$convex.hull.area ~  pheno.collect$genotype)
boxplot(pheno.collect$perimeter ~  pheno.collect$genotype)
boxplot(pheno.collect$longest.path ~  pheno.collect$genotype)
boxplot(pheno.collect$width ~  pheno.collect$genotype)
boxplot(pheno.collect$ellipse.major.axis.length ~ pheno.collect$genotype)

boxplot(area ~ genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect)
qplot(geom = 'boxplot',genotype, area, data = pheno.collect)

#' # SIDE PERSPECTIVE IMAGE
#' This reads the side picturs, not really RGB. Not sure if I want to use anything from this
#' but we have it so here it is.

## get data
file.list <- list.files("output/")
file.list <- file.list[grep("cam0side_results.txt",file.list)]


## open one temp file
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
tmp$observations$genotype$value

pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
  pheno.tmp <- NULL
  for (i in 1:length(tmp$observations)){
    pheno.tmp <- c(pheno.tmp,mean(tmp$observations[[i]]$value))
    
  }
  pheno.collect[j,] <- pheno.tmp
}
colnames(pheno.collect) <- trait.list
rownames(pheno.collect) <- file.list
pheno.collect[1:5,1:5]
pheno.collect <- data.frame(pheno.collect)

#' RANDOM NICE PLOTS
plot(pheno.collect$area.above.reference)
plot(pheno.collect$area)

boxplot(area ~ genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect)
boxplot(pheno.collect$longest.path ~ pheno.collect$genotype)
boxplot(pheno.collect$height ~ pheno.collect$genotype)
qplot(geom = 'boxplot',genotype, area, data = pheno.collect)

############################################################# SIDE PERSPECTIVE 3D data
## get data
file.list <- list.files("output/")
file.list <- file.list[grep("3D_side_results.txt",file.list)]

## open one temp file
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
tmp$observations$genotype$value

pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
  pheno.tmp <- NULL
  for (i in 1:length(tmp$observations)){
    pheno.tmp <- c(pheno.tmp,mean(tmp$observations[[i]]$value))
    
  }
  pheno.collect[j,] <- pheno.tmp
}
colnames(pheno.collect) <- trait.list
rownames(pheno.collect) <- file.list
pheno.collect[1:5,1:5]
pheno.collect <- data.frame(pheno.collect)

#' RANDOM NICE PLOTS
plot(pheno.collect$area.above.reference)
plot(pheno.collect$area)

boxplot(area ~ genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect)
boxplot(pheno.collect$longest.path ~ pheno.collect$genotype)
boxplot(pheno.collect$height ~ pheno.collect$genotype)
qplot(geom = 'boxplot',genotype, area, data = pheno.collect)


#' #Volume thingy
#' The volume calculation does not work at the moment. It does give the soft error that
#' the general position assumption is not met (which is correct). But I am not sure this
#' is the cause of the volume calculation error because I don't see how that is logic.
punten <- read.csv("~/rens2/input/0030_2018-03-14 14.21 - 238A_0_3D.csv", header=FALSE)


View(punten)
x <- cbind(punten[,1], punten[,2], punten[,3])
ashape3d.obj <- ashape3d(x, alpha = 0.75, pert = TRUE)
components_ashape3d(ashape3d.obj, 1)
plot(ashape3d.obj, byComponents = TRUE)
volume_ashape3d(ashape3d.obj, byComponents = TRUE)
    
