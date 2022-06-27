FROM python:3.9

WORKDIR /src/project_files

COPY requirements.txt /src
RUN pip install --no-cache-dir -r /src/requirements.txt

EXPOSE 8888

ENTRYPOINT ["jupyter", "lab", "--ip=0.0.0.0", "--NotebookApp.token=''", "--NotebookApp.password=''", "--allow-root"]
