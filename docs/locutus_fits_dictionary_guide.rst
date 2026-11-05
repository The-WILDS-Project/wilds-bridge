Locutus FITS Dictionary Guide
==========================

This guide is for clients that need observatory metadata for FITS headers or
other data products. Locutus maintains the latest configured telemetry and
turns a named FITS dictionary into a response addressed to the requesting
agent. It does not write a FITS file or apply the values to one; the client
uses the returned values as appropriate.

All topics and examples below use the LDT facility (``joe``) broker path.

Topics and request flow
-----------------------

Use these four topics:

===========================  ==============================================
Purpose                      Topic
===========================  ==============================================
Discover Locutus readiness   ``lorax.ldt.locutus.inforequest``
Receive readiness reply      ``lorax.ldt.locutus.infobroadcast``
Request a FITS dictionary    ``lorax.ldt.locutus.dictrequest``
Receive the dictionary       ``lorax.ldt.locutus.dictresponse``
===========================  ==============================================

Subscribe to the response topic before publishing its corresponding request.
The reply is a broker message; it is not a synchronous RPC response. In
particular, several agents can share ``dictresponse``, so a client must retain
its request ID and accept only a response whose ``recipient`` and
``request_id`` match its own request.

1. Discover readiness and dictionary names
------------------------------------------

Send an ``agentCommand`` message to
``lorax.ldt.locutus.inforequest``. Locutus needs ``sender``, ``hostname``,
``pid``, and ``command`` to parse this form; the common Lorax header fields
shown below are the canonical message form. ``recipient`` is conventional and
makes the intention clear. The command content is not interpreted for this
request, so ``INFO`` is a suitable value.

.. code-block:: xml

   <?xml version="1.0" encoding="utf-8"?>
   <agentCommand>
     <message_id>ca9bda5c-7ce2-4e9f-9636-60ece2f1ba0d</message_id>
     <timestamput>2026-08-14 19:42:31.123</timestamput>
     <loraxver>0.0.dev0</loraxver>
     <hostname>my-client.lowell.local</hostname>
     <platform>Linux</platform>
     <pid>4242</pid>
     <sender>my_fits_client</sender>
     <recipient>Locutus</recipient>
     <command>INFO</command>
   </agentCommand>

Locutus publishes this example response to
``lorax.ldt.locutus.infobroadcast``:

.. code-block:: xml

   <?xml version="1.0" encoding="utf-8"?>
   <agentCommand>
     <message_id>4a86c7a1-351a-4c11-9b86-4d0b6b8c1d00</message_id>
     <timestamput>2026-08-14 19:42:31.165</timestamput>
     <loraxver>0.0.dev0</loraxver>
     <hostname>lo-ldt-locutus.lowell.local</hostname>
     <platform>Linux</platform>
     <pid>107</pid>
     <sender>Locutus</sender>
     <recipient>my_fits_client</recipient>
     <command>READY</command>
     <available_dictionaries>deveny_sv</available_dictionaries>
     <available_dictionaries>deveny_sv_idlgui</available_dictionaries>
     <available_dictionaries>ldt_facility</available_dictionaries>
     <available_dictionaries>ldtboresight_sm</available_dictionaries>
     <available_dictionaries>ldtboresight_uw</available_dictionaries>
     <available_dictionaries>ldtboresight_wb</available_dictionaries>
     <available_dictionaries>ldtboresight_wr</available_dictionaries>
   </agentCommand>

``READY`` says that the dictionary server received and handled the inquiry. The
repeated ``available_dictionaries`` elements are the extensionless names of
TOML files directly in Locutus's ``fits_dicts`` directory. They are the names
to use in ``dictionary_name`` below.

2. Request a dictionary
-----------------------

Generate a new request ID for every request, subscribe to
``lorax.ldt.locutus.dictresponse``, and publish the following exact request
form to ``lorax.ldt.locutus.dictrequest``. ``dictionary_name`` may be the
extensionless name advertised by the information response; for example,
``ldt_facility``.

.. code-block:: xml

   <?xml version="1.0" encoding="utf-8"?>
   <locutusDictRequest>
     <message_id>05ced825-e0de-4ab7-968d-203997c414c6</message_id>
     <timestamput>2026-08-14 19:42:35.001</timestamput>
     <loraxver>0.0.dev0</loraxver>
     <hostname>my-client.lowell.local</hostname>
     <platform>Linux</platform>
     <pid>4242</pid>
     <sender>my_fits_client</sender>
     <recipient>Locutus</recipient>
     <requester>my_fits_client</requester>
     <request_id>ad1e735e-7e5a-4f8e-8a1a-a9312b5b3b13</request_id>
     <dictionary_name>ldt_facility</dictionary_name>
   </locutusDictRequest>

For this request, Locutus publishes a ``locutusDict`` response on
``lorax.ldt.locutus.dictresponse``. The outer ``locutusDict`` carries routing
and correlation fields. The nested ``locutusDict`` holds FITS keyword tables;
each keyword supplies ``val``, ``comment``, and ``valid``.

.. code-block:: xml

   <?xml version="1.0" encoding="utf-8"?>
   <locutusDict>
     <message_id>29c714d5-d7de-4719-8e4d-98bea6fb0acd</message_id>
     <timestamput>2026-08-14 19:42:35.047</timestamput>
     <loraxver>0.0.dev0</loraxver>
     <hostname>lo-ldt-locutus.lowell.local</hostname>
     <platform>Linux</platform>
     <pid>107</pid>
     <sender>Locutus</sender>
     <request_id>ad1e735e-7e5a-4f8e-8a1a-a9312b5b3b13</request_id>
     <dictionary_name>ldt_facility</dictionary_name>
     <recipient>my_fits_client</recipient>
     <locutusDict>
       <OBSERVAT>
         <val>Lowell Observatory</val>
         <comment>observatory</comment>
         <valid>true</valid>
       </OBSERVAT>
       <PRESSURE>
         <val>785.2</val>
         <comment>Air Pressure in mBars, Adjusted to Sea Level</comment>
         <valid>true</valid>
       </PRESSURE>
       <TELRA>
         <val>12:34:56.78</val>
         <comment>TCS right ascension (hh:mm:ss)</comment>
         <valid>true</valid>
       </TELRA>
     </locutusDict>
   </locutusDict>

A client should first match both ``recipient`` and ``request_id``. It may then
add each nested keyword to its FITS header using ``val`` and ``comment``.
``valid`` is ``false`` when Locutus could not obtain or derive a value; use the
returned value (often the dictionary's default) according to your product's
missing-data policy. Responses can contain many more keywords than shown.

If the dictionary cannot be loaded, the response retains ``request_id``,
``dictionary_name``, and ``recipient`` but has an ``error`` element instead of
the nested dictionary:

.. code-block:: xml

   <locutusDict>
     <request_id>ad1e735e-7e5a-4f8e-8a1a-a9312b5b3b13</request_id>
     <dictionary_name>not_a_dictionary</dictionary_name>
     <recipient>my_fits_client</recipient>
     <error>
       <code>dictionary_not_found</code>
       <message>...</message>
     </error>
   </locutusDict>

Practical client rules
----------------------

* Treat readiness and dictionary traffic as asynchronous broker messages.
* Use a unique request ID for every dictionary request and filter responses by
  both request ID and recipient.
* Request close to the point where the FITS header is finalized; Locutus uses
  cached telemetry and records freshness in ``valid``.
* Keep the dictionary name and its ``KWDICT`` entry in the data product so its
  metadata definition remains traceable.
* Do not use a response addressed to another agent, even when it appears on the
  shared response topic.

Advanced: Defining FITS metadata in TOML
----------------------------------------

A dictionary is a TOML file under ``lorax/locutus/fits_dicts``. A top-level
file is a requestable parent dictionary and appears in the information reply.
Files in a subdirectory, normally ``common/``, are reusable blocks and are
included by a parent dictionary. The required shape is:

.. code-block:: toml

   format_version = 2

   # List every broker topic used by direct entries or helper sources.
   topics = ["Ryans.DCTWeatherStream"]

   [[entries]]
   keyword = "EXAMPLE"
   topic = "Ryans.DCTWeatherStream"
   paths = ["DCTweather.mtTemp1"]
   default = "UNKNOWN"
   comment = "Example FITS metadata"
   precision = 2

A direct entry reads one cached value. ``keyword``, ``topic``, ``paths``,
``default``, and ``comment`` are required. ``precision`` is optional and rounds
numeric results. ``paths`` is a list because Locutus accepts a sequence of
candidate flattened paths; it uses the first available value. For XML broker
messages, paths use dotted element names, such as
``DeviceStatus.status.exptime``. A literal value uses an empty topic and path
list:

.. code-block:: toml

   [[entries]]
   keyword = "TELESCOP"
   topic = ""
   paths = []
   default = "Lowell Discovery Telescope"
   comment = "Telescope name"

Reuse common definitions at the desired position in the output with an include
entry. The include path is relative to the dictionary that names it; include
entries contain no other keys.

.. code-block:: toml

   [[entries]]
   include = ["common/ldt_telescope", "common/ldt_weather"]

For transformations that need multiple values, use a registered helper. Helper
entries require format version 2, a non-empty ``sources`` list, and each source
must name a topic in the top-level ``topics`` list. A source's ``view`` is
optional: ``SX`` (the default) uses the last-known value, while ``S`` requires
a current/fresh value.

.. code-block:: toml

   [[entries]]
   keyword = "PRESSURE"
   helper = "units.inches_hg_to_mbar"
   sources = [
     { name = "inches_hg", topic = "Ryans.DCTWeatherStream", path = "DCTweather.mtAdjBaromPress" },
   ]
   default = "UNKNOWN"
   comment = "Air pressure in mbar, adjusted to sea level"
   precision = 1

Adding a needed value
---------------------

1. Ask for the existing parent dictionaries and choose an appropriate one, or
   create a new top-level ``.toml`` file when the metadata belongs to a new
   instrument or product.
2. Identify the source broker topic and the flattened payload path. Existing
   dictionaries are practical templates: ``common/ldt_weather.toml`` shows
   direct weather values and helpers, while ``common/ldt_telescope.toml``
   shows coordinate and telescope metadata.
3. Add the source topic to ``topics`` and add one direct or helper ``entries``
   table. Give every FITS keyword a useful default and comment; duplicate
   keywords, duplicate topics, malformed fields, and unsupported helper
   arguments are rejected.
4. Validate the TOML by requesting the dictionary and check the returned
   ``valid`` values. A new top-level file will be listed by ``inforequest``;
   a common block is available only through a parent that includes it.

A dictionary only describes how Locutus maps telemetry it already monitors. It
does **not** subscribe Locutus to a new broker topic. If the desired source
topic is not already monitored, request that the Locutus configuration owner
add it to ``topics_to_monitor`` with its parser, schema if applicable, and
freshness timeout. Once that configured telemetry is being collected, a TOML
entry can expose it to FITS-header clients.
