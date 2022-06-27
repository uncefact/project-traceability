
# build stage
#FROM public.ecr.aws/lambda/python:3.10 AS builder
FROM python:3.10 AS builder

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock /project/
COPY src/ /project/src

# install dependencies and project
WORKDIR /project
RUN pdm sync --prod --no-editable


# run stage
FROM python:3.10

# retrieve packages from build stage
ENV PYTHONPATH=/project/pkgs
COPY --from=builder /project/__pypackages__/3.10/lib /project/pkgs

# set command/entrypoint, adapt to fit your needs
CMD ["python", "project/src/itc_api.py"]
