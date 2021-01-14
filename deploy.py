from pyspark.sql import SparkSession
header_text = "source,isTrueDirect,sourceKeyword,medium,isVideoAd,fullVisitorId,visitId,date,newVisits,hitReferer,hitType,hitAction_type,hitNumber,hitHour,hitMin,timeMicroSec,v2ProductName,productListName,isClick,isImpression,sessionQualityDim,timeOnScreen,timeOnSite,totalTransactionRevenue"
from pyspark.sql.types import *
attr_list = []
for each_attr in header_text.split(','):
    attr_list.append(StructField(each_attr, StringType(), True))
custom_schema = StructType(attr_list)


# coding: utf-8

# In[1]:

#spark


# In[ ]:

#spark.stop()


# In[ ]:

spark = SparkSession     .builder     .appName("Funnel")     .master("yarn")     .config("spark.total.executor.cores","12")    .config("spark.executor.memory","1G")    .getOrCreate();
spark.sparkContext.setLogLevel("ERROR");

# In[ ]:

#raw_df = spark.read.format('csv').schema(custom_schema).option('header','true').option('mode','DROPMALFORMED').load('/user/rawzone/funnel/*')
raw_df = spark.read.format('csv').schema(custom_schema).option('header','true').option('mode','DROPMALFORMED').load('/user/rawzone/funnel-sqoop-toHDFS/*')

# In[ ]:

mem_raw_df = raw_df.repartition(60).cache()


# ### Numbers of Rows

# In[ ]:

#mem_raw_df.count()


# In[ ]:

mem_raw_df.columns


# In[ ]:

allCol_list = mem_raw_df.columns


# In[ ]:

removeCol_list = ['timeOnScreen']


# In[ ]:

for i in removeCol_list:
    allCol_list.remove(i)


# In[ ]:

newCol_list = []


# In[ ]:

newCol_list = allCol_list


# In[ ]:

filtered_raw_df = mem_raw_df.select(newCol_list)


# # 2. Data Preparation

# ## Data Cleansing: Remove missing values

# In[ ]:

from pyspark.sql.functions import udf
from pyspark.sql.types import *


# ### Remove Null

# In[ ]:

def f_removenull(origin):
    if origin == None:
        return 'NULL'
    else:
        return origin


# In[ ]:

removenull = udf(lambda x: f_removenull(x),StringType())


# ### Make Binary

# In[ ]:

def f_makebinary(origin):
    if origin == None:
        return 'FALSE'
    elif origin == 'true':
        return 'TRUE'
    elif origin == '1':
        return 'TRUE'
    else:
        return 'NULL'


# In[ ]:

makebinary = udf(lambda x: f_makebinary(x),StringType())


# In[ ]:




# In[ ]:




# ### Clean Null with Zero

# In[ ]:

def f_cleanNullwithZero(item):
    if item == None:
        new = '0'
        return new
    else:
        return item


# In[ ]:

cleanNullwithZero = udf(lambda x:f_cleanNullwithZero(x),StringType())


# ### Make Dollar

# In[ ]:

def f_makedollar(revenue):
    if revenue == None:
        return 0
    else:
        return revenue/1000000


# In[ ]:

makedollar = udf(lambda x: f_makedollar(x),FloatType())


# In[ ]:

from pyspark.sql.functions import col


# In[ ]:

#filtered_raw_df.describe().toPandas().transpose()


# In[ ]:

crunched_df = filtered_raw_df.withColumn('hitHour',col('hitHour').cast(FloatType())).withColumn('hitMin',col('hitMin').cast(FloatType())).withColumn('hitNumber',col('hitNumber').cast(FloatType())).withColumn('timeMicroSec',col('timeMicroSec').cast(FloatType())).withColumn('timeOnSite',col('timeOnSite').cast(FloatType())).withColumn('totalTransactionRevenue',cleanNullwithZero(col('totalTransactionRevenue')).cast(FloatType())).withColumn('newVisits',makebinary(col('newVisits'))).withColumn('sourceKeyword',removenull(col('sourceKeyword'))).withColumn('isVideoAd',makebinary(col('isVideoAd'))).withColumn('hitReferer',removenull(col('hitReferer'))).withColumn('isClick',makebinary(col('isClick'))).withColumn('isImpression',makebinary(col('isImpression'))).withColumn('sessionQualityDim',removenull(col('sessionQualityDim'))).withColumn('timeOnSite',removenull(col('timeOnSite'))).withColumn('totalTransactionRevenue',makedollar(col('totalTransactionRevenue'))).withColumn('isTrueDirect',makebinary(col('isTrueDirect')))


# In[ ]:

#crunched_df.describe().toPandas().transpose()


# In[ ]:

#crunched_df.filter(col('fullVisitorId') == '0131989137375171234').filter(col('visitId') == '1493252333').show()


# ### Summary within Partition

# In[ ]:

#importing libraries
#from sklearn.datasets import load_boston
#import pandas as pd
#import numpy as np
#import matplotlib
#import matplotlib.pyplot as plt
#import seaborn as sns
#import statsmodels.api as sm
#get_ipython().magic('matplotlib inline')
#from sklearn.model_selection import train_test_split
#from sklearn.linear_model import LinearRegression
#from sklearn.feature_selection import RFE
#from sklearn.linear_model import RidgeCV, LassoCV, Ridge, Lasso


# In[ ]:

#from com.crealytics.spark.excel import *
from pyspark.sql.functions import col, udf, sum
from pyspark.sql.types import *
from pyspark.sql import Row
from pyspark.sql.window import Window


# In[ ]:

crunched_df


# In[ ]:

crunched_df.columns


# In[ ]:

import sys


# In[ ]:

from pyspark.sql.types import *


# In[ ]:

from pyspark.sql.functions import *


# In[ ]:

w = Window()   .partitionBy('fullVisitorId','visitId')   .orderBy(col("hitNumber").cast("long"))


# In[ ]:

windowSpec = Window.partitionBy('fullVisitorId','visitId').orderBy(col("hitNumber").cast("long")).rangeBetween(-sys.maxsize, sys.maxsize)


# In[ ]:

from pyspark.sql import functions as func


# In[ ]:

Diff_hitNumber = func.max(col('hitNumber').cast(IntegerType())).over(windowSpec) - func.min(col('hitNumber').cast(IntegerType())).over(windowSpec)


# In[ ]:

Diff_timeMicroSec = func.max(col('timeMicroSec').cast(IntegerType())).over(windowSpec) - func.min(col('timeMicroSec').cast(IntegerType())).over(windowSpec)


# In[ ]:

Diff_hitHour = func.max(col('hitHour').cast(IntegerType())).over(windowSpec) - func.min(col('hitHour').cast(IntegerType())).over(windowSpec)


# In[ ]:

Diff_hitMin = func.max(col('hitMin').cast(IntegerType())).over(windowSpec) - func.min(col('hitMin').cast(IntegerType())).over(windowSpec)


# In[ ]:

first_hitNumber = func.first(col('hitNumber').cast(IntegerType())).over(windowSpec)


# In[ ]:

last_hitNumber = func.last(col('hitNumber').cast(IntegerType())).over(windowSpec)


# In[ ]:

first_Action_type = func.first(col('hitAction_type').cast(StringType())).over(windowSpec)


# In[ ]:

last_Action_type = func.last(col('hitAction_type').cast(StringType())).over(windowSpec)


# In[ ]:

from pyspark.sql.functions import to_timestamp


# In[ ]:

partitionCal_df = crunched_df.withColumn('first_hitNumber', first_hitNumber).withColumn('last_hitNumber', last_hitNumber).withColumn('Diff_hitNumber', Diff_hitNumber).withColumn('Diff_timeMicroSec', Diff_timeMicroSec).withColumn('Diff_hitHour', Diff_hitHour).withColumn('Diff_hitMin', Diff_hitMin).withColumn('first_Action_type', first_Action_type).withColumn('last_Action_type', last_Action_type).dropna()


# In[ ]:

partitionCal_df.columns


# In[ ]:

partitionCal_df.columns


# In[ ]:

partitionCal_df.columns


# In[ ]:

def f_removeLastItem(list):
    list.pop()
    return list


# In[ ]:

removeLastItem = func.udf(lambda x:removeLastItem(x))


# In[ ]:

collectList_df = partitionCal_df.groupBy([
'source',
 ##'isTrueDirect',
 ##'sourceKeyword',
 ##'medium',
 'isVideoAd',
 'fullVisitorId',
 'visitId',
 #'date',
 ##'newVisits',
 ##'hitReferer',
 #'hitType',
 #'hitAction_type',
 #'hitNumber',
 #'hitHour',
 #'hitMin',
 #'timeMicroSec',
 #'v2ProductName',
 #'productListName',
 #'isClick',
 #'isImpression',
 ##'sessionQualityDim',
 #'timeOnSite',
 #'totalTransactionRevenue',
 'first_hitNumber',
 'last_hitNumber',
 'Diff_hitNumber',
 'Diff_timeMicroSec',
 'Diff_hitHour',
 'Diff_hitMin',
 'first_Action_type',
 'last_Action_type']).agg(func.collect_list('hitAction_type'))\
#.withColumn('collect_list(hitAction_type)',removeLastItem(col('collect_list(hitAction_type)')))

# In[ ]:

#raw_df.select(['fullVisitorId','visitId']).distinct().count()


# In[ ]:

#collectList_df.count()


# # EDA

# ##### The action type. Click through of product lists = 1, Product detail views = 2, Add product(s) to cart = 3, Remove product(s) from cart = 4, Check out = 5, Completed purchase = 6, Refund of purchase = 7, Checkout options = 8, Unknown = 0.



# In[ ]:

funnel_col_list = collectList_df.columns


# In[ ]:

funnel_col_list


# In[ ]:

raw_funnel_df = collectList_df.select(['fullVisitorId',
 'visitId',
 'first_hitNumber',
 'last_hitNumber',
 'Diff_hitNumber',
 'Diff_hitHour',
 'Diff_hitMin',
 'Diff_timeMicroSec',
 'first_Action_type',
 'last_Action_type',
 'collect_list(hitAction_type)'])


# In[ ]:




# ### Declare Functions for Removing Duplication and Last items in List

# In[ ]:

def f_removedupINLIST(l):
    seen = set()
    new_list = [x for x in l if not (x in seen or seen.add(x))]
    new_list.pop()
    return new_list


# In[ ]:

removedupINLIST = func.udf(lambda x: f_removedupINLIST(x))


# In[ ]:

raw_funnel_df.columns


# In[ ]:

f_length_list = func.udf(lambda x: len(x),IntegerType())


# In[ ]:

seq_funnel_df = raw_funnel_df.withColumn('seq_hitAction_type',removedupINLIST(col('collect_list(hitAction_type)'))).withColumn('length_hitAction_type',f_length_list(col('collect_list(hitAction_type)')))


# In[ ]:

seq_funnel_df.columns


# In[ ]:

seq_funnel_df


# ##### The action type. Click through of product lists = 1, Product detail views = 2, Add product(s) to cart = 3, Remove product(s) from cart = 4, Check out = 5, Completed purchase = 6, Refund of purchase = 7, Checkout options = 8, Unknown = 0.

# In[ ]:

seq_funnel_df.printSchema()


# In[ ]:

seq_funnel_df.count()


# In[ ]:

final_df = seq_funnel_df


# In[ ]:

#final_df.select(['fullVisitorId','visitId']).distinct().count()


# In[ ]:

#final_df.count()


# # 3. Data Modeling

# In[ ]:

import pyspark
from pyspark.sql import SQLContext
from pyspark.sql.types import *
from pyspark.ml.feature import OneHotEncoder, StringIndexer
from pyspark.ml.feature import VectorAssembler
from pyspark.mllib.clustering import KMeans, KMeansModel
from pyspark.ml.feature import StringIndexer, VectorAssembler, OneHotEncoder,VectorIndexer, QuantileDiscretizer
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, BinaryClassificationEvaluator
from pyspark.ml.classification import LogisticRegression, GBTClassifier, NaiveBayes, RandomForestClassifier, DecisionTreeClassifier
from pyspark.ml import Pipeline
from pyspark.ml.clustering import *
from pyspark.ml.feature import Bucketizer


# In[ ]:

def get_evaluation(trainingSet,testingSet,algo,                   categoricalCols,continuousCols,discretedCols,split_range,labelCol):

    from pyspark.ml import Pipeline
    from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
    from pyspark.sql.functions import col
    
    
    labelIndexer = StringIndexer(inputCol=labelCol,                             outputCol='indexedLabel',                             handleInvalid='keep')

    indexers = [ StringIndexer(handleInvalid='keep',                               inputCol=c, outputCol="{0}_indexed".format(c))
                 for c in categoricalCols ]

    # default setting: dropLast=True
    encoders = [ OneHotEncoder(inputCol=indexer.getOutputCol(),
                 outputCol="{0}_encoded".format(indexer.getOutputCol()))
                 for indexer in indexers ]
    discretizers = [ Bucketizer(inputCol=d, outputCol="{0}_discretized".format(d)                 ,splits=split_range)
                 for d in discretedCols ]
    
    
    featureCols = ['features']
    assembler = VectorAssembler(inputCols=[encoder.getOutputCol() for encoder in encoders]
                                + continuousCols +\
                                [discretizer.getOutputCol() for discretizer in discretizers], \
                                outputCol='features')
    
    
    #var_name = algo
    ml_algorithm = algo(featuresCol='features',                                labelCol='indexedLabel')
    


    
    pipeline = Pipeline(stages=[labelIndexer] + indexers + encoders + discretizers +                         [assembler] + [ml_algorithm])
    
    

    model=pipeline.fit(trainingSet)
    result_df = model.transform(testingSet)
    evaluator_RF = MulticlassClassificationEvaluator(predictionCol="prediction",                                              labelCol='indexedLabel', metricName='accuracy')
    print(algo,'====>',evaluator_RF.evaluate(result_df)*100)

    return model


# In[ ]:

final_df.printSchema()


# In[ ]:

final_df.columns


# In[ ]:

catcols = ['first_Action_type',
           'seq_hitAction_type'
          ]

num_cols = ['first_hitNumber',
 'last_hitNumber',
 'Diff_hitNumber',
 'Diff_hitHour',
 'Diff_hitMin',
 'Diff_timeMicroSec',
            'length_hitAction_type'
           ]

discols = [           #'pub_rec',\
           #'seq_hitAction_type'\
          ]



labelCol = 'last_Action_type'

splits = [-1.0, 0.0, 10.0, 20.0, 30.0, 40.0, float("inf")]

selected_algo = [DecisionTreeClassifier, RandomForestClassifier, LogisticRegression]
#selected_algo = [LogisticRegression]


# In[ ]:

training_df, testing_df = final_df.randomSplit(weights = [0.80, 0.20], seed = 13)


# In[ ]:

for a in selected_algo:
    model = get_evaluation(training_df,testing_df,a,catcols,num_cols,discols, splits, labelCol)


# In[ ]:

testing_df.count()


# In[ ]:

#testing_df.groupBy('last_Action_type').count().orderBy('last_Action_type').show()


# In[ ]:

#model.transform(testing_df).filter(col('indexedLabel') == col('prediction')).groupBy('last_Action_type','indexedLabel','prediction').count().orderBy('last_Action_type').show()


# In[ ]:

#model.transform(testing_df).filter(col('indexedLabel') != col('prediction')).groupBy('last_Action_type','indexedLabel','prediction').count().orderBy('last_Action_type').show()


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



model.write().overwrite().save('/user/refinedzone/model')
