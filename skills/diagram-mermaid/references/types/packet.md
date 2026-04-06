# Packet Diagram

**Directive:** `packet-beta`

**Syntax:**

```
packet-beta
    0-15: "Field Name"
    16-31: "Another Field"
    32-47: "Third Field"
```

**Example:**

```
%% Diagram: TCP Header
%% Type: packet
packet-beta
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
    96-99: "Data Offset"
    100-102: "Reserved"
    103-103: "NS"
    104-104: "CWR"
    105-105: "ECE"
    106-106: "URG"
    107-107: "ACK"
    108-108: "PSH"
    109-109: "RST"
    110-110: "SYN"
    111-111: "FIN"
    112-127: "Window Size"
```
