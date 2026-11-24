# Everything the tests need: the OpenSP SGML parser, Python and pytest.
#
#   podman build -t edgar-sgml .
#   podman run --rm -v "$PWD":/repo:ro,Z edgar-sgml
#
# (docker works the same way.)
FROM registry.fedoraproject.org/fedora-minimal:latest
RUN microdnf -y install opensp python3 python3-pytest && microdnf clean all
WORKDIR /repo
CMD ["python3", "-m", "pytest", "-p", "no:cacheprovider"]
