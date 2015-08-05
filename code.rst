Code
====

The code is organised into packages, in the standard django way.

.. graphviz::

   digraph d {
      node [shape=folder];
      disco_service [label="<project>\ndisco_service"];
      crawler [label="<app>\ncrawler"];
      metadata [label="<app>\nmetadata"];
      govservices [label="<app>\ngovservices"];

      disco_service -> crawler;
      disco_service -> metadata;
      disco_service -> govservices;

   }

The following documentation is incomplete (work in progress), for the timebeing it's better to reffer to the actual sources.

.. automodule:: disco_service

.. automodule:: crawler

.. automodule:: metadata

.. automodule:: govservices


