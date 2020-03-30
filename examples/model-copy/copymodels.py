ws1 = Workspace.from_config()
ws2 = Workspace.from_config("config/for/otherws")

for model in Model.list(ws1):
  serialized = model.serialize()
  path = model.download(exist_ok=True)
  rehydrated = Model.register(ws2,
                              model_path=path,
                              model_name=serialized["name"],
                              tags=serialized["tags"],
                              properties={'officialVersion':serialized["version"]})
