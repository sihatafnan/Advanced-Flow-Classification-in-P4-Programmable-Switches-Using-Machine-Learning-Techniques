# Advanced Flow Classification in P4 Programmable Switches Using Machine Learning Techniques

Network flow classification entirely in the data plane of a **P4** programmable switch. A machine-learning model (decision tree / random forest) is trained offline on packet flow features, then its learned decision rules are compiled into match-action rules and thresholds that run directly on the switch, so packets are classified at line rate without sending them to a controller.

## How It Works

1. **Traffic generation & feature extraction** (`traffic/`) - synthetic/replayed traffic is sent and received between hosts, and per-flow features are extracted (protocol, source/destination ports, packet size, packet count, inter-arrival time).
2. **Preprocessing** (`preprocess/`) - the raw flow data is cleaned, useless properties are removed, and the dataset is split into train/test batches.
3. **Model training** (`algorithm/`) - a decision tree (`dt_rk.py`) or random forest (`random_forest_rk.py`) is trained with scikit-learn. The learned tree is exported as per-feature threshold lists and "when ... then class" rules so it can be expressed as switch table entries.
4. **Data-plane deployment** (`p4code/`) - the P4 program implements the classification logic; `algorithm/mycontroller.py` populates the switch tables with the rules derived from the trained model.

## Repository Structure

```
algorithm/      ML models and the P4 control-plane program
  dt_rk.py            Decision-tree training; exports thresholds + lineage rules
  random_forest_rk.py Random-forest training
  mycontroller.py     Controller that installs table entries on the switch
  check_tree.txt      Exported decision rules
preprocess/     Dataset preparation
  convert_flow.py, remove_useless_prop.py, split_data_rk.py,
  make_test_batches.py, make_data_for_Raf.py
traffic/        Traffic generation, capture, and results analysis
  send-traffic.py, recieve-traffic.py, traffic_distribution.py,
  distribute-host-flows.py, readResults.py, genGraph.py, Dockerfile
p4code/         P4 source, network config, and BMv2/utils tooling
  src/, net/, install/, utils/
```

## Features

- In-network (data-plane) flow classification on P4 programmable switches.
- Decision-tree and random-forest classifiers translated into switch match-action rules.
- Flow features: protocol, TCP/UDP source and destination ports, packet size, packet count, and inter-arrival time.
- Tooling for traffic generation, dataset preprocessing, and results visualization.

## Tech Stack

- **P4** for the switch data plane (BMv2 behavioral model, Mininet-based topology under `p4code/`)
- **Python** with **scikit-learn**, **numpy**, and **pandas** for model training
- **pydotplus** / graphviz for decision-tree export
- **matplotlib** for graphing results
- **Docker** (`traffic/Dockerfile`) for the traffic-generation environment

## Usage

Train a decision tree from a flow dataset and export switch rules:
```
python algorithm/dt_rk.py -i <path-to-dataset.csv> -o <rules-output.txt>
```

Compile and run the P4 program from `p4code/` (BMv2 + Mininet), then install the learned rules onto the switch:
```
python algorithm/mycontroller.py
```

Generate and capture traffic, then analyze results using the scripts in `traffic/`.
