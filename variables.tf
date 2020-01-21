variable "name" {
  description = "Name of the function payload thing"
}

variable "project_path" {
  description = "Path to the function directory"
}

variable "output_path" {
  description = "Where to write the payload zip"
}

# Optional settings

variable "runtime" {
  default     = "python3.7"
  description = "Python runtime. defaults to 3.7."
}

variable "requirements_file" {
  default     = ""
  description = "The path to the requirements file. Can be empty."
}

variable "lib_path" {
  default     = ""
  description = "Path to common python files directory"
}
