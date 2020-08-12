import openml
import sklearn
from sklearn.metrics import roc_auc_score, accuracy_score, mean_squared_error

flow_id = 6970
task_id = 233

flow = openml.flows.get_flow(flow_id, reinstantiate=True, strict_version=False)
task = openml.tasks.get_task(task_id)

dataset = task.get_dataset()
tti = task.task_type_id    
ep = task.estimation_procedure_id
em = task.evaluation_measure

model = flow.model

X, y, categorical_indicator, attribute_names = dataset.get_data(
    dataset_format='array',
    target=dataset.default_target_attribute
)

model.fit(X, y)
preds = model.predict(X)
score = mean_squared_error(y, preds)


result = {
    'flow': flow_id,
    'task': task_id,
    'score': score
}

print(result)