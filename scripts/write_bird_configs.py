import os

base = '/home/ubuntu/network-automation/bird-configs'

configs = {
'SP1': """router id 10.0.0.1;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.1.1.0/30 blackhole;
    route 10.1.2.0/30 blackhole;
    route 10.1.3.0/30 blackhole;
    route 10.1.4.0/30 blackhole;
}
protocol bgp upstream { local 10.0.1.2 as 65001; neighbor 10.0.1.1 as 65000; ipv4 { import all; export all; }; }
protocol bgp sp4 { local 10.1.1.1 as 65001; neighbor 10.1.1.2 as 65004; ipv4 { import all; export all; }; }
protocol bgp sp5 { local 10.1.2.1 as 65001; neighbor 10.1.2.2 as 65005; ipv4 { import all; export all; }; }
protocol bgp sp6 { local 10.1.3.1 as 65001; neighbor 10.1.3.2 as 65006; ipv4 { import all; export all; }; }
protocol bgp sp7 { local 10.1.4.1 as 65001; neighbor 10.1.4.2 as 65007; ipv4 { import all; export all; }; }
""",
'SP2': """router id 10.0.0.2;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.2.1.0/30 blackhole;
    route 10.2.2.0/30 blackhole;
    route 10.2.3.0/30 blackhole;
    route 10.2.4.0/30 blackhole;
}
protocol bgp upstream { local 10.0.2.2 as 65001; neighbor 10.0.2.1 as 65000; ipv4 { import all; export all; }; }
protocol bgp sp4 { local 10.2.1.1 as 65001; neighbor 10.2.1.2 as 65004; ipv4 { import all; export all; }; }
protocol bgp sp5 { local 10.2.2.1 as 65001; neighbor 10.2.2.2 as 65005; ipv4 { import all; export all; }; }
protocol bgp sp6 { local 10.2.3.1 as 65001; neighbor 10.2.3.2 as 65006; ipv4 { import all; export all; }; }
protocol bgp sp7 { local 10.2.4.1 as 65001; neighbor 10.2.4.2 as 65007; ipv4 { import all; export all; }; }
""",
'SP3': """router id 10.0.0.3;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.3.1.0/30 blackhole;
    route 10.3.2.0/30 blackhole;
    route 10.3.3.0/30 blackhole;
    route 10.3.4.0/30 blackhole;
}
protocol bgp upstream { local 10.0.3.2 as 65001; neighbor 10.0.3.1 as 65000; ipv4 { import all; export all; }; }
protocol bgp sp4 { local 10.3.1.1 as 65001; neighbor 10.3.1.2 as 65004; ipv4 { import all; export all; }; }
protocol bgp sp5 { local 10.3.2.1 as 65001; neighbor 10.3.2.2 as 65005; ipv4 { import all; export all; }; }
protocol bgp sp6 { local 10.3.3.1 as 65001; neighbor 10.3.3.2 as 65006; ipv4 { import all; export all; }; }
protocol bgp sp7 { local 10.3.4.1 as 65001; neighbor 10.3.4.2 as 65007; ipv4 { import all; export all; }; }
""",
'SP4': """router id 10.0.0.4;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.4.1.0/30 blackhole;
}
protocol bgp sp1 { local 10.1.1.2 as 65004; neighbor 10.1.1.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp2 { local 10.2.1.2 as 65004; neighbor 10.2.1.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp3 { local 10.3.1.2 as 65004; neighbor 10.3.1.1 as 65001; ipv4 { import all; export all; }; }
""",
'SP5': """router id 10.0.0.5;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.4.2.0/30 blackhole;
}
protocol bgp sp1 { local 10.1.2.2 as 65005; neighbor 10.1.2.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp2 { local 10.2.2.2 as 65005; neighbor 10.2.2.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp3 { local 10.3.2.2 as 65005; neighbor 10.3.2.1 as 65001; ipv4 { import all; export all; }; }
""",
'SP6': """router id 10.0.0.6;
protocol kernel { ipv4 { export all; import all; }; }
prot
