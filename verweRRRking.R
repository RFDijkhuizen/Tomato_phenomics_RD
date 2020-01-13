library(rjson)
library(stringr)
library(ggplot2)
library(alphashape3d)
library(stringr)
setwd("~/rens2")

#
# 3D TOP results 
# Ik laat de rest voor nu nog even weg omdat het anders wel overcrowded wordt.

# Get all files in a list
file.list <- list.files("output/")
file.list <- file.list[grep("3D_top_results.txt",file.list)]

# Open one file to get dimensions
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))
trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
trait.list <- c("sample_name", trait.list)

# Create dataframe for observations
pheno.collect <- data.frame(matrix(NA,nrow = 0,ncol = length(trait.list)), stringsAsFactors = FALSE)
colnames(pheno.collect) <- trait.list
names3D <- c()
# Now loop over the data and insert values into the dataframe
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
  if( length(tmp$observations)==33){ # check if there are enough observations, so only fully scored plants are in the dataset
    sample_name <- str_replace(file.list[j],"(^.+ - .+)_3D.*$", "\\1") # Start by adding the sample name as trait. get the sample name from file name with 
    pheno.tmp <- sample_name 
    names3D <- c(names3D, sample_name)
    for (i in 1:length(tmp$observations)){ # Loop over values and add them to vector
    
    ## So there are traits with more than 1 value, to prevent errors we (useing paste) concatenate those values together separated by ; (so we can split later on)
    ## posiible issue later on is that values will be stored as text/string/characters, we need to as.numeric() them when we want to plot/do stats...
    
    pheno.tmp <- cbind(pheno.tmp, paste(tmp$observations[[i]]$value,collapse = ";")) # 
  }
  # Add new observation here
  #pheno.tmp <- data.frame(pheno.tmp, stringsAsFactors = FALSE)
  colnames(pheno.tmp) <- trait.list
  pheno.collect <- rbind(pheno.collect, pheno.tmp, stringsAsFactors = FALSE) # Now the pheno.tmp has only one row ;-)
}}

pheno.collect <- data.frame(pheno.collect, stringsAsFactors = FALSE)
rownames(pheno.collect) <- names3D
dim(pheno.collect)

## simple plots
this <- ggplot(pheno.collect,aes(as.numeric(pheno.collect$solidity)))+
        geom_histogram(bins = 100)
this

this <- ggplot(pheno.collect,aes(as.numeric(pheno.collect$area)))+
  geom_histogram(bins = 100)
this

this <- ggplot(pheno.collect,aes(as.numeric(pheno.collect$area),as.numeric(pheno.collect$perimeter)))+
  geom_point()+
  geom_smooth()
this

this <- ggplot(pheno.collect,aes(as.numeric(pheno.collect$longest.path)))+
  geom_histogram(bins = 100)
this

med.trait <- aggregate(as.numeric(pheno.collect$area),list(pheno.collect$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect$genotype <- factor(pheno.collect$genotype,levels = ril.ord)

this <- ggplot(pheno.collect,aes(pheno.collect$genotype,as.numeric(pheno.collect$area)))+
  geom_boxplot()
this

med.trait <- aggregate(as.numeric(pheno.collect$perimeter),list(pheno.collect$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect$genotype <- factor(pheno.collect$genotype,levels = ril.ord)

this <- ggplot(pheno.collect,aes(pheno.collect$genotype,as.numeric(pheno.collect$perimeter)))+
  geom_boxplot()
this

med.trait <- aggregate(as.numeric(pheno.collect$solidity),list(pheno.collect$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect$genotype <- factor(pheno.collect$genotype,levels = ril.ord)

this <- ggplot(pheno.collect,aes(pheno.collect$genotype,as.numeric(pheno.collect$solidity)))+
  geom_boxplot()
this


################## Loop for side 3D data #################################################################

# Get all files in a list
file.list <- list.files("output/")
file.list <- file.list[grep("3D_side_results.txt",file.list)]

# Open one file to get dimensions
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))
trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
trait.list <- c("sample_name", trait.list)

# Create dataframe for observations
pheno.collect.side3D <- data.frame(matrix(NA,nrow = 0,ncol = length(trait.list)), stringsAsFactors = FALSE)
colnames(pheno.collect.side3D) <- trait.list
names3D <- c()
# Now loop over the data and insert values into the dataframe
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
  if( length(tmp$observations)==30){ # check if there are enough observations, so only fully scored plants are in the dataset
    sample_name <- str_replace(file.list[j],"(^.+ - .+)_3D.*$", "\\1") # Start by adding the sample name as trait. get the sample name from file name with 
    pheno.tmp <- sample_name 
    names3D <- c(names3D, sample_name)
    for (i in 1:length(tmp$observations)){ # Loop over values and add them to vector
      
      ## So there are traits with more than 1 value, to prevent errors we (useing paste) concatenate those values together separated by ; (so we can split later on)
      ## posiible issue later on is that values will be stored as text/string/characters, we need to as.numeric() them when we want to plot/do stats...
      
      pheno.tmp <- cbind(pheno.tmp, paste(tmp$observations[[i]]$value,collapse = ";")) # 
    }
    # Add new observation here
    #pheno.tmp <- data.frame(pheno.tmp, stringsAsFactors = FALSE)
    colnames(pheno.tmp) <- trait.list
    pheno.collect.side3D <- rbind(pheno.collect.side3D, pheno.tmp, stringsAsFactors = FALSE) # Now the pheno.tmp has only one row ;-)
  }}

pheno.collect.side3D <- data.frame(pheno.collect.side3D, stringsAsFactors = FALSE)
rownames(pheno.collect.side3D) <- names3D
dim(pheno.collect.side3D)

## simple plots
this <- ggplot(pheno.collect.side3D,aes(as.numeric(pheno.collect.side3D$solidity)))+
  geom_histogram(bins = 100)
this

this <- ggplot(pheno.collect.side3D,aes(as.numeric(pheno.collect.side3D$area)))+
  geom_histogram(bins = 100)
this

this <- ggplot(pheno.collect.side3D,aes(as.numeric(pheno.collect$area),as.numeric(pheno.collect$perimeter)))+
  geom_point()+
  geom_smooth()
this

this <- ggplot(pheno.collect.side3D,aes(as.numeric(pheno.collect.side3D$longest.path)))+
  geom_histogram(bins = 100)
this

med.trait <- aggregate(as.numeric(pheno.collect.side3D$area),list(pheno.collect.side3D$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect.side3D$genotype <- factor(pheno.collect.side3D$genotype,levels = ril.ord)

this <- ggplot(pheno.collect.side3D,aes(pheno.collect.side3D$genotype,as.numeric(pheno.collect.side3D$area)))+
  geom_boxplot()
this

med.trait <- aggregate(as.numeric(pheno.collect.side3D$perimeter),list(pheno.collect.side3D$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect.side3D$genotype <- factor(pheno.collect.side3D$genotype,levels = ril.ord)

this <- ggplot(pheno.collect.side3D,aes(pheno.collect.side3D$genotype,as.numeric(pheno.collect.side3D$perimeter)))+
  geom_boxplot()
this

med.trait <- aggregate(as.numeric(pheno.collect.side3D$solidity),list(pheno.collect.side3D$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect.side3D$genotype <- factor(pheno.collect.side3D$genotype,levels = ril.ord)

this <- ggplot(pheno.collect.side3D,aes(pheno.collect.side3D$genotype,as.numeric(pheno.collect.side3D$solidity)))+
  geom_boxplot()
this


################### 3D Volume thingy ####################################################################
# currently just for one plant as test.
#
#punten <- read.csv("~/rens2/input/0030_2018-03-14 14.21 - 238A_0_3D.csv", header=FALSE)
#x <- cbind(punten[,1], punten[,2], punten[,3])
#ashape3d.obj <- ashape3d(x, alpha = 1, pert = TRUE)
#components_ashape3d(ashape3d.obj, 1)
#plot(ashape3d.obj, byComponents = TRUE)
#volume_ashape3d(ashape3d.obj, byComponents = FALSE, indexAlpha = 'all')


################## 3D volume calculation ################################################################
file.list <- list.files("input/")
file.list <- file.list[grep("3D.csv", file.list)]
pheno.volumes <- numeric()
namesVOL <- c()
for (j in 1:length(file.list)){
  tmp <- read.csv(paste0(c("input/",file.list[j]),collapse = ""), header=FALSE)
  if(length(tmp[,1])>1 & length(tmp[,2])>1 & length(tmp[,3])>1 & (length(tmp[,1]) + length(tmp[,2]) + length(tmp[,3])) > 1000){ 
    # Only really useful when the 3d model has a lot of points, so skip otherwise.
  tmp <- cbind(tmp[,1], tmp[,2], tmp[,3])
    suppressWarnings(tmp <- ashape3d(tmp, alpha = 1, pert = TRUE)) # Surpresses the General position assumption warning
    components_ashape3d(tmp, 1)
    tmp <- volume_ashape3d(tmp, byComponents = FALSE, indexAlpha = 'all')
    pheno.volumes <- c(pheno.volumes, tmp)
    sample_name <- str_replace(file.list[j],"(^.+ - .+)_3D.*$", "\\1") # Get the sample name to crossreference with other dataframes
    namesVOL <- c(namesVOL, sample_name)
  }
}

pheno.volumes <- data.frame(pheno.volumes)
colnames(pheno.volumes) <- "Volume"
rownames(pheno.volumes) <- namesVOL

################## Loop for top cam data #################################################################


# Get all files in a list
file.list <- list.files("output/")
file.list <- file.list[grep("cam9top_results",file.list)]

# Open one file to get dimensions
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))
trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
trait.list <- c("sample_name", trait.list)

# Create dataframe for observations
pheno.collect2 <- data.frame(matrix(NA,nrow = 0,ncol = length(trait.list)), stringsAsFactors = FALSE)
colnames(pheno.collect2) <- trait.list
names <- c()
# Now loop over the data and insert values into the dataframe
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
  if( length(tmp$observations)==36){ # check if there are enough observations, so only fully scored plants are in the dataset
    sample_name <- str_replace(file.list[j],"(^.+ - .+)_cam9.*$", "\\1") # Start by adding the sample name as trait. get the sample name from file name with 
    sample_name <- paste(sample_name, "_0", sep = "")
    pheno.tmp <- sample_name 
    names <- c(names, sample_name)
    for (i in 1:length(tmp$observations)){ # Loop over values and add them to vector
      
      ## So there are traits with more than 1 value, to prevent errors we (useing paste) concatenate those values together separated by ; (so we can split later on)
      ## posiible issue later on is that values will be stored as text/string/characters, we need to as.numeric() them when we want to plot/do stats...
      
      pheno.tmp <- cbind(pheno.tmp, paste(tmp$observations[[i]]$value,collapse = ";")) # 
      #pheno.tmp <- cbind(pheno.tmp, tmp$observations[[i]]$value)
    }
    # Add new observation here
    colnames(pheno.tmp) <- trait.list
    pheno.collect2 <- rbind(pheno.collect2, pheno.tmp, stringsAsFactors = FALSE) # Now the pheno.tmp has only one row ;-)
  }}

pheno.collect2 <- data.frame(pheno.collect2, stringsAsFactors = FALSE)
rownames(pheno.collect2) <- names
dim(pheno.collect2)

## simple plots
this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$solidity)))+
  geom_histogram(bins = 100)
this

this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$area)))+
  geom_histogram(bins = 100)
this

med.trait <- aggregate(as.numeric(pheno.collect2$area),list(pheno.collect2$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect2$genotype <- factor(pheno.collect2$genotype,levels = ril.ord)

this <- ggplot(pheno.collect2,aes(pheno.collect2$genotype,as.numeric(pheno.collect2$area)))+
  geom_boxplot()
this

## some color data stuff, extract the counts [0-255] --> green 
tmp <- sapply(pheno.collect2$green.frequencies,strsplit,";")
names(tmp) <- pheno.collect2$sample_name
green.counts <- matrix(as.numeric(unlist(tmp)),ncol = 256)

tot.cnt <- apply(green.counts,1,sum)
val.sum <- apply(t(apply(green.counts,1,"*",0:255)),1,sum)
ave.green <- val.sum/tot.cnt

pheno.collect2 <- data.frame(pheno.collect2,ave.green)


this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$ave.green)))+
  geom_histogram(bins = 100)
this


this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$area),as.numeric(pheno.collect2$ave.green)))+
  geom_point()+
  geom_smooth()
this

med.trait <- aggregate(as.numeric(pheno.collect2$ave.green),list(pheno.collect2$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect2$genotype <- factor(pheno.collect2$genotype,levels = ril.ord)

this <- ggplot(pheno.collect2,aes(pheno.collect2$genotype,as.numeric(pheno.collect2$ave.green)))+
  geom_boxplot()
this


##---> red

tmp <- sapply(pheno.collect2$red.frequencies,strsplit,";")
names(tmp) <- pheno.collect2$sample_name
red.counts <- matrix(as.numeric(unlist(tmp)),ncol = 256)

tot.cnt <- apply(red.counts,1,sum)
val.sum <- apply(t(apply(red.counts,1,"*",0:255)),1,sum)
ave.red <- val.sum/tot.cnt

pheno.collect2 <- data.frame(pheno.collect2,ave.red)


this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$ave.red)))+
  geom_histogram(bins = 100)
this


this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$ave.red)/as.numeric(pheno.collect2$ave.green)))+
  geom_histogram(bins = 100)
this



this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$ave.red),as.numeric(pheno.collect2$ave.green)))+
  geom_point()+
  geom_smooth()
this

med.trait <- aggregate(as.numeric(pheno.collect2$ave.red),list(pheno.collect2$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect2$genotype <- factor(pheno.collect2$genotype,levels = ril.ord)

this <- ggplot(pheno.collect2,aes(pheno.collect2$genotype,as.numeric(pheno.collect2$ave.red)))+
  geom_boxplot()
this


med.trait <- aggregate(as.numeric(pheno.collect2$ave.red)/as.numeric(pheno.collect2$ave.green),list(pheno.collect2$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect2$genotype <- factor(pheno.collect2$genotype,levels = ril.ord)

this <- ggplot(pheno.collect2,aes(pheno.collect2$genotype,log2(as.numeric(pheno.collect2$ave.red)/as.numeric(pheno.collect2$ave.green))))+
  geom_boxplot()
this


#### Final Frame ####################
trait.listfinal <- c("sample_name", "top surface", "top convex hull", "top convex vertices", "top solidity", "top height", "top width","top perimeter",
                     "leafs seen from top", "top number of cycles", "top longest path", "top ellipse major axis length", "top ellipse minor axis length",
                     "top ellipse major axis angle", "top ellipse eccentricity", "top average leaf angle", "top sd leaf angle", "top average leaf length",
                     "top sd leaf length", "top average stem angle", "top sd stem angle", "top average stem length", "top sd stem length",
                     "side area", "side convex hull", "side convex vertices", "side solidity", "side height", "side width", "side perimeter",
                     "side number of cycles", "side longest path", "side ellipse major axis length", "side ellipse minor axis length",
                     "side ellipse major axis angle", "side ellipse eccentricity", "side average leaf angle", "side sd leaf angle",
                     "side average stem angle", "side sd stem angle",
                     "average green value", "sd green values", "average red value",  "sd red values", "average blue value", "sd blue values",
                     "average hue value", "sd hue values", "average saturation value", "sd saturation values", "average value value", "sd value values",
                     "average lightness value", "sd lightness values", "average green-magenta value", "sd green-magenta values",
                     "average blue-yellow value", "sd blue-yellow values", "volume" ,"genotype")                                                         # Final phenotype list
names.listfinal <- Reduce(intersect, list(names3D,names,namesVOL))                                           # List of samples that abide by both the 3D definition and the cam definition 

pheno.collectfinal <- data.frame(matrix(NA,nrow = 0,ncol = length(trait.listfinal)), stringsAsFactors = FALSE)
# In this loop all interesting traits will be inserted one by one.
for (name in names.listfinal){ # The 1:1000 is a temporary subset for development
  # First everything simple we can learn from top perspective
  newrow <- data.frame(pheno.collect[name, "sample_name"])
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "area"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "convex.hull.area"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "convex.hull.vertices"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "solidity"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "height"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "width"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "perimeter"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "estimated.object.count"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "number.of.cycles"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "longest.path"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "ellipse.major.axis.length"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "ellipse.minor.axis.length"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "ellipse.major.axis.angle"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect[name, "ellipse.eccentricity"]))
  # Now everything complex we need to get trough further calculations from top perspective
  newrow <- data.frame(newrow, mean(abs(as.numeric(unlist(str_split(pheno.collect[name, "top_leaf_angles"], ";"))))))
  newrow <- data.frame(newrow, sd(abs(as.numeric(unlist(str_split(pheno.collect[name, "top_leaf_angles"], ";"))))))
  newrow <- data.frame(newrow, mean(abs(as.numeric(unlist(str_split(pheno.collect[name, "top_leaf_lengths"], ";"))))))
  newrow <- data.frame(newrow, sd(abs(as.numeric(unlist(str_split(pheno.collect[name, "top_leaf_lengths"], ";"))))))
  newrow <- data.frame(newrow, mean(abs(as.numeric(unlist(str_split(pheno.collect[name, "top_stem_angles"], ";"))))))
  newrow <- data.frame(newrow, sd(abs(as.numeric(unlist(str_split(pheno.collect[name, "top_stem_angles"], ";"))))))
  newrow <- data.frame(newrow, mean(abs(as.numeric(unlist(str_split(pheno.collect[name, "top_stem_lengths"], ";"))))))
  newrow <- data.frame(newrow, sd(abs(as.numeric(unlist(str_split(pheno.collect[name, "top_stem_lengths"], ";"))))))
  # Now some simply traits we see from side perspective
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "area"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "convex.hull.area"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "convex.hull.vertices"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "solidity"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "height"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "width"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "perimeter"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "number.of.cycles"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "longest.path"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "ellipse.major.axis.length"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "ellipse.minor.axis.length"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "ellipse.major.axis.angle"]))
  newrow <- data.frame(newrow, as.numeric(pheno.collect.side3D[name, "ellipse.eccentricity"]))
  # Now everything complex we need to get trough further calculations from side perspective
  newrow <- data.frame(newrow, mean(abs(as.numeric(unlist(str_split(pheno.collect.side3D[name, "side_leaf_angles"], ";"))))))
  newrow <- data.frame(newrow, sd(abs(as.numeric(unlist(str_split(pheno.collect.side3D[name, "side_leaf_angles"], ";"))))))
  newrow <- data.frame(newrow, mean(abs(as.numeric(unlist(str_split(pheno.collect.side3D[name, "side_stem_angles"], ";"))))))
  newrow <- data.frame(newrow, sd(abs(as.numeric(unlist(str_split(pheno.collect.side3D[name, "side_stem_angles"], ";"))))))
  # Now come the colors. For now we take the average amount of green or red in a leaf when you take the RGB values from all pixels considered plant.
  colortemp <- t(as.numeric(unlist(str_split(pheno.collect2[name, "green.frequencies"], ";"))))  # GREEN
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))
  colortemp <- as.numeric(unlist(str_split(pheno.collect2[name, "red.frequencies"], ";")))    # RED
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))
  colortemp <- as.numeric(unlist(str_split(pheno.collect2[name, "blue.frequencies"], ";")))   # BLUE
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))
  ## That was the RGB color space, now let's take a look at the HSV color space
  colortemp <- as.numeric(unlist(str_split(pheno.collect2[name, "hue.frequencies"], ";")))  # HUE
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))
  colortemp <- as.numeric(unlist(str_split(pheno.collect2[name, "saturation.frequencies"], ";")))  # SATURATION
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))
  colortemp <- as.numeric(unlist(str_split(pheno.collect2[name, "value.frequencies"], ";")))   # VALUE
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))
  # Now pure for completionist sake we can also add the CIELAB color space as we measured it anyway
  colortemp <- as.numeric(unlist(str_split(pheno.collect2[name, "lightness.frequencies"], ";")))   # LIGHTNESS
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))
  colortemp <- as.numeric(unlist(str_split(pheno.collect2[name, "green.magenta.frequencies"], ";")))  # GREEN_MAGENTA
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))
  
  colortemp <- as.numeric(unlist(str_split(pheno.collect2[name, "blue.yellow.frequencies"], ";")))  # BLUE_YELLOW
  colorcount <- 0
  colorvalues <- numeric()
  for (i in colortemp){
    tmp <- rep(colorcount, times = i)
    colorvalues <- c(colorvalues, tmp)
    colorcount <- colorcount + 1
  }
  newrow <- data.frame(newrow, mean(colorvalues))
  newrow <- data.frame(newrow, sd(colorvalues))

  ## Now lastly the volume and genotype  
  newrow <- data.frame(newrow, pheno.volumes[name, "Volume"])
  newrow <- data.frame(newrow, pheno.collect[name, "genotype"])
  # bind this newrow to the final dataframe
  print(name) # Just to keep track where you are
  pheno.collectfinal <- rbind(pheno.collectfinal, newrow, stringsAsFactors = FALSE)
  

}
colnames(pheno.collectfinal) <- trait.listfinal
rownames(pheno.collectfinal) <- names.listfinal

pheno.collectfinal[1:5, 2:length(trait.listfinal)]
#### END ############################



#### KLAD

## some color data stuff, extract the counts [0-255] --> green 
#tmp <- sapply(pheno.collect2$green.frequencies,strsplit,";")
#names(tmp) <- pheno.collect2$sample_name
#green.counts <- matrix(as.numeric(unlist(tmp)),ncol = 256)

#tot.cnt <- apply(green.counts,1,sum)
#val.sum <- apply(t(apply(green.counts,1,"*",0:255)),1,sum)
#ave.green <- val.sum/tot.cnt



