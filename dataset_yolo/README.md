# dataset_yolo - training data (YOLO format)

Dataset used to train `models/best_model.pt` (Subsystem 1/2).

| Split | Images |
|---|---|
| train | 827 |
| val | 146 |
| test | 50 |

* 7 classes (`data.yaml`): Biomuell, Glass, Metal, Papier, Plastic, Sondermuell, Textile_Trash
* Layout: `images/<split>/*.jpg|png` and `labels/<split>/*.txt` (one YOLO box per line: `class x_center y_center width height`, normalised 0-1)
* Train with Ultralytics: `yolo detect train data=dataset_yolo/data.yaml model=yolo11n.pt` (use your own base model)
* Image sources (e.g. RealWaste, TrashPanda) and their licences must be confirmed on the original dataset pages before publishing.
