workflow "New workflow" {
  on = "push"
  resolves = ["Create python wheel"]
}

action "Create python wheel" {
  uses = "docker://python:3.7"
  runs = "python setup.py --help"
}
