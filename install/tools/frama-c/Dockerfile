FROM ubuntu:20.04

USER root
WORKDIR /build

RUN apt-get update -y                                 \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git                                               \
    ocaml                                             \
    opam                                              \
    ocaml-native-compilers                            \
    liblablgtk2-ocaml-dev                             \
    liblablgtksourceview2-ocaml-dev                   \
    libocamlgraph-ocaml-dev                           \
    libyojson-ocaml-dev                               \
    libocamlgraph-ocaml-dev                           \
    libzarith-ocaml-dev                               \
    build-essential                                   \
    libfindlib-ocaml                                  \
    libocamlgraph-ocaml-dev                           \
    libzarith-ocaml                                   \
    libyojson-ocaml-dev                               \
    autoconf                                          \
    debianutils                                       \
    graphviz                                          \
    libexpat1-dev                                     \
    libgmp-dev                                        \
    libgnomecanvas2-dev                               \
    libgtk2.0-dev                                     \
    libgtksourceview2.0-dev                           \
    m4                                                \
    perl                                              \
    pkg-config                                        \
    zlib1g-dev                                        \
    libgtksourceview2.0-0                             \
    linux-headers-generic                             \
    libc6-dev-i386                                    \
 && groupadd -r frama-c                               \
 && useradd --no-log-init -m -r -g frama-c frama-c    \
 && rm -rf /var/lib/apt/lists/*

USER frama-c
WORKDIR /src
RUN opam init -a --disable-sandboxing                 \
 && eval $(opam env)                                  \
 && opam install -y depext                            \
 && opam depext -y frama-c                            \
 && opam install -y frama-c                           \
 && echo "eval \$(opam env)" >> ~/.bashrc

USER frama-c
RUN echo "eval \$(opam env)"   >> ~/.bash_profile

