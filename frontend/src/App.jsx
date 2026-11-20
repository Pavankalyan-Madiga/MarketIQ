
import { useEffect, useState } from "react";

import {
  Users,
  IndianRupee,
  ShoppingCart,
  UserPlus,
  LayoutDashboard,
  ChartNoAxesCombined,
  BrainCircuit,
  ShoppingBag,
  MessageSquareText,
  Bot,
  Database,
  Settings,
  Bell,
  Search,
  RefreshCw,
  AlertCircle,
  Upload,
  FileSpreadsheet,
  Eye,
  Trash2,
  X,
  CheckCircle2,
  ClipboardCheck,
  Package,
  UserRoundSearch,
  ShoppingBasket,
  ShieldAlert,
  Activity,
  Target,
  UserRound,
  Palette,
  Moon,
  Sun,
  Save,
  RotateCcw,
  Info,
  Server,
  Mail,
} from "lucide-react";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";

import {
  getDashboardStats,
  getRevenue,
  getSegments,
  getCustomers,
  getCustomer,
  getSegmentationSummary,
  getSegmentationDistribution,
  getSegmentCustomers,
  getDatasets,
  uploadDataset,
  previewDataset,
  deleteDataset,
  validateDataset,
  getDatasetQualityOverview,
  getRecommendationSummary,
  getPopularProducts,
  getCustomerRecommendations,
  getFrequentlyBoughtTogether,
  getChurnSummary,
  getChurnCustomers,
  getChurnModelInfo,
  getSentimentSummary,
  getSentimentDistribution,
  getSentimentTrends,
  getSentimentReviews,
} from "./services/api";

import "./App.css";

const navigation = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Customers", icon: Users },
  { name: "Segmentation", icon: ChartNoAxesCombined },
  { name: "Predictions", icon: BrainCircuit },
  { name: "Recommendations", icon: ShoppingBag },
  { name: "Sentiment Analysis", icon: MessageSquareText },
  { name: "AI Assistant", icon: Bot },
  { name: "Datasets", icon: Database },
  { name: "Data Quality", icon: ClipboardCheck },
];

const colors = ["#4F46E5", "#0D9488", "#F59E0B", "#EF4444"];

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">CM</div>

        <div>
          <h2>MarketIQ</h2>
          <span>Customer Intelligence</span>
        </div>
      </div>

      <div className="nav-label">WORKSPACE</div>

      <nav>
        {navigation.map((item) => {
          const Icon = item.icon;

          return (
            <button
              type="button"
              key={item.name}
              className={`nav-item ${
                activePage === item.name ? "active" : ""
              }`}
              onClick={() => onNavigate(item.name)}
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <button
          type="button"
          className={`nav-item ${
            activePage === "Settings" ? "active" : ""
          }`}
          onClick={() => onNavigate("Settings")}
        >
          <Settings size={19} />
          <span>Settings</span>
        </button>

        <div className="profile">
          <div className="avatar">PK</div>

          <div>
            <strong>Admin User</strong>
            <span>Administrator</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

function StatCard({ title, value, icon: Icon }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{title}</span>

        <div className="stat-icon">
          <Icon size={20} />
        </div>
      </div>

      <h2>{value}</h2>

      <div className="stat-change">
        <span>Actual database data</span>
      </div>
    </div>
  );
}

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [revenue, setRevenue] = useState([]);
  const [segments, setSegments] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      try {
        setLoading(true);
        setError("");

        const [statsData, revenueData, segmentData] =
          await Promise.all([
            getDashboardStats(),
            getRevenue(),
            getSegments(),
          ]);

        if (!cancelled) {
          setStats(statsData);
          setRevenue(revenueData);
          setSegments(segmentData);
        }
      } catch (err) {
        console.error("Dashboard API error:", err);

        if (!cancelled) {
          setError(
            "Unable to load dashboard data. Please check whether FastAPI and PostgreSQL are running."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  if (loading) {
    return (
      <main className="main-content">
        <div className="loading-state">
          <RefreshCw size={24} className="spin" />
          <h2>Loading dashboard...</h2>
          <p>Fetching data from PostgreSQL</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="main-content">
        <div className="error-state">
          <AlertCircle size={32} />
          <h2>Dashboard unavailable</h2>
          <p>{error}</p>

          <button
            type="button"
            onClick={() => setRefreshKey((value) => value + 1)}
          >
            <RefreshCw size={16} />
            Retry
          </button>
        </div>
      </main>
    );
  }

  const totalSegmentCustomers = segments.reduce(
    (total, item) => total + Number(item.value),
    0
  );

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>Dashboard</h1>
            <p>Welcome back! Here's your business overview.</p>
          </div>
        </div>

        <div className="topbar-actions">
          <button className="icon-button" aria-label="Search">
            <Search size={19} />
          </button>

          <button className="icon-button" aria-label="Notifications">
            <Bell size={19} />
          </button>

          <button
            className="icon-button"
            aria-label="Refresh dashboard"
            onClick={() => setRefreshKey((value) => value + 1)}
          >
            <RefreshCw size={18} />
          </button>

          <div className="date-filter">Database Overview</div>
        </div>
      </header>

      {/* KPI CARDS */}

      <section className="stats-grid">
        <StatCard
          title="Total Revenue"
          value={formatCurrency(stats.total_revenue)}
          icon={IndianRupee}
        />

        <StatCard
          title="Total Customers"
          value={stats.total_customers.toLocaleString("en-IN")}
          icon={Users}
        />

        <StatCard
          title="Total Orders"
          value={stats.total_orders.toLocaleString("en-IN")}
          icon={ShoppingCart}
        />

        <StatCard
          title="New Customers"
          value={stats.new_customers.toLocaleString("en-IN")}
          icon={UserPlus}
        />
      </section>

      {/* ANALYTICS */}

      <section className="analytics-grid">
        {/* REVENUE CHART */}

        <div className="panel revenue-panel">
          <div className="panel-header">
            <div>
              <h3>Revenue Overview</h3>
              <p>Monthly delivered-order revenue</p>
            </div>
          </div>

          <div className="revenue-total">
            {formatCurrency(stats.total_revenue)}
          </div>

          <div className="chart-container">
            {revenue.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={revenue}
                  margin={{
                    top: 10,
                    right: 15,
                    left: 10,
                    bottom: 5,
                  }}
                >
                  <defs>
                    <linearGradient
                      id="revenueGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="5%"
                        stopColor="#4F46E5"
                        stopOpacity={0.22}
                      />

                      <stop
                        offset="95%"
                        stopColor="#4F46E5"
                        stopOpacity={0}
                      />
                    </linearGradient>
                  </defs>

                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="month"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <YAxis
                    tickFormatter={(value) =>
                      `₹${(value / 100000).toFixed(0)}L`
                    }
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                  />

                  <Tooltip
                    formatter={(value) => [
                      formatCurrency(value),
                      "Revenue",
                    ]}
                  />

                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stroke="#4F46E5"
                    strokeWidth={3}
                    fill="url(#revenueGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <p>No revenue data available.</p>
            )}
          </div>
        </div>

        {/* CUSTOMER SEGMENTS */}

        <div className="panel segment-panel">
          <div className="panel-header">
            <div>
              <h3>Customer Segments</h3>
              <p>Distribution by delivered orders</p>
            </div>
          </div>

          <div className="pie-container">
            {segments.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={segments}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={65}
                    outerRadius={95}
                    paddingAngle={4}
                  >
                    {segments.map((item, index) => (
                      <Cell
                        key={item.name}
                        fill={colors[index % colors.length]}
                      />
                    ))}
                  </Pie>

                  <Tooltip
                    formatter={(value, name) => [
                      `${Number(value).toLocaleString("en-IN")} customers`,
                      name,
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p>No segment data available.</p>
            )}
          </div>

          <div className="segment-legend">
            {segments.map((segment, index) => {
              const percentage =
                totalSegmentCustomers > 0
                  ? (segment.value / totalSegmentCustomers) * 100
                  : 0;

              return (
                <div className="legend-item" key={segment.name}>
                  <div>
                    <span
                      className="legend-dot"
                      style={{
                        background: colors[index % colors.length],
                      }}
                    />

                    {segment.name}
                  </div>

                  <strong>
                    {percentage.toFixed(1)}%
                  </strong>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* RECENT ORDERS */}

      <section className="panel orders-panel">
        <div className="panel-header">
          <div>
            <h3>Recent Orders</h3>
            <p>Order management will be implemented next.</p>
          </div>
        </div>
      </section>

      <footer className="footer">
        Customer Behavior & Marketing Intelligence
        <span>PostgreSQL connected · Synthetic dataset</span>
      </footer>
    </main>
  );
}


function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState("");
  const [detailsError, setDetailsError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadCustomers() {
      try {
        setLoading(true);
        setError("");

        const data = await getCustomers(search, page, 10);

        if (!cancelled) {
          setCustomers(data.customers);
          setPagination(data.pagination);
        }
      } catch (err) {
        console.error("Customers API error:", err);

        if (!cancelled) {
          setError(
            "Unable to load customers. Check whether the backend is running."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadCustomers();

    return () => {
      cancelled = true;
    };
  }, [search, page]);

  async function openCustomer(customerId) {
    try {
      setDetailsLoading(true);
      setDetailsError("");
      setSelectedCustomer(null);

      const data = await getCustomer(customerId);
      setSelectedCustomer(data);
    } catch (err) {
      console.error("Customer details API error:", err);
      setDetailsError("Unable to load customer details.");
    } finally {
      setDetailsLoading(false);
    }
  }

  function closeCustomerDetails() {
    setSelectedCustomer(null);
    setDetailsError("");
  }

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>Customers</h1>
            <p>Manage and explore your customer database.</p>
          </div>
        </div>
      </header>

      <section className="panel customers-panel">
        <div className="customers-toolbar">
          <div>
            <h3>All Customers</h3>
            <p>
              {pagination
                ? `${pagination.total.toLocaleString("en-IN")} customers`
                : "Customer directory"}
            </p>
          </div>

          <label className="customer-search">
            <Search size={18} />
            <input
              type="search"
              placeholder="Search name, email or city..."
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
            />
          </label>
        </div>

        {loading ? (
          <div className="customers-message">
            <RefreshCw size={22} className="spin" />
            <span>Loading customers...</span>
          </div>
        ) : error ? (
          <div className="customers-message customers-error">
            <AlertCircle size={22} />
            <span>{error}</span>
          </div>
        ) : customers.length === 0 ? (
          <div className="customers-message">
            <Users size={24} />
            <span>No customers found.</span>
          </div>
        ) : (
          <>
            <div className="table-wrapper customers-table-wrapper">
              <table className="customers-table">
                <thead>
                  <tr>
                    <th>Customer</th>
                    <th>Customer ID</th>
                    <th>City</th>
                    <th>Age</th>
                    <th>Gender</th>
                    <th>Membership</th>
                    <th>Signup Date</th>
                  </tr>
                </thead>
                <tbody>
                  {customers.map((customer) => (
                    <tr
                      key={customer.customer_id}
                      className="customer-row"
                      onClick={() => openCustomer(customer.customer_id)}
                    >
                      <td>
                        <div className="customer-name">{customer.name}</div>
                        <div className="customer-email">{customer.email}</div>
                      </td>
                      <td className="customer-id">{customer.customer_id}</td>
                      <td>{customer.city}</td>
                      <td>{customer.age}</td>
                      <td>{customer.gender}</td>
                      <td>
                        <span
                          className={`membership-badge ${String(
                            customer.membership
                          ).toLowerCase()}`}
                        >
                          {customer.membership}
                        </span>
                      </td>
                      <td>{customer.signup_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="customers-pagination">
              <span>
                Showing {customers.length} of{" "}
                {pagination.total.toLocaleString("en-IN")} customers
              </span>

              <div className="pagination-actions">
                <button
                  type="button"
                  disabled={page <= 1}
                  onClick={() => setPage((current) => current - 1)}
                >
                  Previous
                </button>
                <span>
                  {pagination.page} / {pagination.total_pages}
                </span>
                <button
                  type="button"
                  disabled={page >= pagination.total_pages}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </section>

      {detailsLoading && (
        <div className="customer-modal-overlay">
          <div className="customer-modal customers-message">
            <RefreshCw size={22} className="spin" />
            <span>Loading customer details...</span>
          </div>
        </div>
      )}

      {detailsError && (
        <div
          className="customer-modal-overlay"
          onClick={() => setDetailsError("")}
        >
          <section
            className="customer-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <button
              className="modal-close"
              type="button"
              onClick={() => setDetailsError("")}
              aria-label="Close"
            >
              ×
            </button>
            <div className="customers-message customers-error">
              <AlertCircle size={22} />
              <span>{detailsError}</span>
            </div>
          </section>
        </div>
      )}

      {selectedCustomer && (
        <div
          className="customer-modal-overlay"
          onClick={closeCustomerDetails}
        >
          <section
            className="customer-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <button
              className="modal-close"
              type="button"
              onClick={closeCustomerDetails}
              aria-label="Close customer details"
            >
              ×
            </button>

            <div className="customer-modal-heading">
              <div className="customer-modal-avatar">
                {selectedCustomer.name?.charAt(0)?.toUpperCase() || "C"}
              </div>
              <div>
                <h2>{selectedCustomer.name}</h2>
                <p>{selectedCustomer.customer_id}</p>
              </div>
            </div>

            <div className="customer-details-grid">
              <div>
                <span>Email</span>
                <strong>{selectedCustomer.email}</strong>
              </div>
              <div>
                <span>City</span>
                <strong>{selectedCustomer.city}</strong>
              </div>
              <div>
                <span>Age</span>
                <strong>{selectedCustomer.age}</strong>
              </div>
              <div>
                <span>Gender</span>
                <strong>{selectedCustomer.gender}</strong>
              </div>
              <div>
                <span>Membership</span>
                <strong>{selectedCustomer.membership}</strong>
              </div>
              <div>
                <span>Signup Date</span>
                <strong>{selectedCustomer.signup_date}</strong>
              </div>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}


const segmentColors = {
  Champions: "#16A34A",
  "Loyal Customers": "#0D9488",
  "Potential Loyalists": "#4F46E5",
  "Recent Customers": "#3B82F6",
  "At Risk": "#F59E0B",
  Hibernating: "#EF4444",
  "Needs Attention": "#8B5CF6",
  "No Delivered Orders": "#64748B",
};

function SegmentationPage() {
  const [summary, setSummary] = useState(null);
  const [distribution, setDistribution] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [segment, setSegment] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadOverview() {
      try {
        setLoading(true);
        setError("");

        const [summaryData, distributionData] = await Promise.all([
          getSegmentationSummary(),
          getSegmentationDistribution(),
        ]);

        if (!cancelled) {
          setSummary(summaryData);
          setDistribution(distributionData);
        }
      } catch (err) {
        console.error("Segmentation overview error:", err);
        if (!cancelled) {
          setError("Unable to load segmentation data. Check the backend and try again.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadOverview();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadSegmentCustomers() {
      try {
        const data = await getSegmentCustomers(segment, search, page, 10);

        if (!cancelled) {
          setCustomers(data.customers);
          setPagination(data.pagination);
        }
      } catch (err) {
        console.error("Segment customers error:", err);
        if (!cancelled) {
          setError("Unable to load segmented customers.");
        }
      }
    }

    loadSegmentCustomers();

    return () => {
      cancelled = true;
    };
  }, [segment, search, page]);

  const formatMoney = (value) => formatCurrency(value);

  if (loading) {
    return (
      <main className="main-content">
        <div className="loading-state">
          <RefreshCw size={24} className="spin" />
          <h2>Loading customer segmentation...</h2>
          <p>Calculating RFM customer metrics</p>
        </div>
      </main>
    );
  }

  if (error && !summary) {
    return (
      <main className="main-content">
        <div className="error-state">
          <AlertCircle size={32} />
          <h2>Segmentation unavailable</h2>
          <p>{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>Customer Segmentation</h1>
            <p>Understand customer value and purchase behaviour using RFM analysis.</p>
          </div>
        </div>
      </header>

      {error && <div className="customers-message customers-error">{error}</div>}

      <section className="stats-grid">
        <StatCard
          title="Total Customers"
          value={summary?.total_customers?.toLocaleString("en-IN") || "0"}
          icon={Users}
        />
        <StatCard
          title="Active Customers"
          value={summary?.active_customers?.toLocaleString("en-IN") || "0"}
          icon={UserPlus}
        />
        <StatCard
          title="Inactive Customers"
          value={summary?.inactive_customers?.toLocaleString("en-IN") || "0"}
          icon={Users}
        />
        <StatCard
          title="Average Recency"
          value={`${summary?.average_recency_days ?? 0} days`}
          icon={RefreshCw}
        />
      </section>

      <section className="analytics-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Customer Segment Distribution</h3>
              <p>Number of customers in each RFM segment</p>
            </div>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distribution} margin={{ top: 10, right: 10, left: 0, bottom: 45 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 10 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="customer_count" name="Customers" radius={[5, 5, 0, 0]}>
                  {distribution.map((item) => (
                    <Cell key={item.name} fill={segmentColors[item.name] || "#64748B"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Segment Revenue</h3>
              <p>Revenue contribution by customer segment</p>
            </div>
          </div>
          <div className="pie-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={distribution}
                  dataKey="revenue"
                  nameKey="name"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={2}
                >
                  {distribution.map((item) => (
                    <Cell key={item.name} fill={segmentColors[item.name] || "#64748B"} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatMoney(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="segment-legend">
            {distribution.map((item) => (
              <div className="legend-item" key={item.name}>
                <div>
                  <span
                    className="legend-dot"
                    style={{ background: segmentColors[item.name] || "#64748B" }}
                  />
                  {item.name}
                </div>
                <strong>{formatMoney(item.revenue)}</strong>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="panel customers-panel">
        <div className="customers-toolbar">
          <div>
            <h3>Segmented Customers</h3>
            <p>
              {pagination ? `${pagination.total.toLocaleString("en-IN")} matching customers` : "RFM customer records"}
            </p>
          </div>
          <div className="customer-search">
            <Search size={18} />
            <input
              type="search"
              placeholder="Search customer, email or city..."
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
            />
          </div>
          <select
            className="segment-filter"
            value={segment}
            onChange={(event) => {
              setSegment(event.target.value);
              setPage(1);
            }}
          >
            <option value="">All segments</option>
            {distribution.map((item) => (
              <option key={item.name} value={item.name}>{item.name}</option>
            ))}
          </select>
        </div>

        <div className="table-wrapper">
          <table className="customers-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Segment</th>
                <th>Recency</th>
                <th>Frequency</th>
                <th>Monetary</th>
                <th>RFM Score</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr
                  key={customer.customer_id}
                  className="customer-row"
                  onClick={() => setSelectedCustomer(customer)}
                >
                  <td>
                    <div className="customer-name">{customer.name}</div>
                    <div className="customer-email">{customer.email}</div>
                  </td>
                  <td>
                    <span
                      className="membership-badge"
                      style={{
                        background: `${segmentColors[customer.segment] || "#64748B"}18`,
                        color: segmentColors[customer.segment] || "#64748B",
                      }}
                    >
                      {customer.segment}
                    </span>
                  </td>
                  <td>{customer.recency_days == null ? "—" : `${customer.recency_days} days`}</td>
                  <td>{customer.frequency}</td>
                  <td>{formatMoney(customer.monetary)}</td>
                  <td><strong>{customer.rfm_score}/15</strong></td>
                </tr>
              ))}
              {!customers.length && (
                <tr>
                  <td colSpan="6">No customers found for this filter.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="customers-pagination">
          <span>
            {pagination
              ? `Showing ${customers.length} of ${pagination.total.toLocaleString("en-IN")} customers`
              : "Loading customer records"}
          </span>
          <div className="pagination-actions">
            <button
              type="button"
              disabled={!pagination || page <= 1}
              onClick={() => setPage((current) => current - 1)}
            >
              Previous
            </button>
            <span>{pagination ? `${pagination.page} / ${pagination.total_pages}` : "—"}</span>
            <button
              type="button"
              disabled={!pagination || page >= pagination.total_pages}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </button>
          </div>
        </div>
      </section>

      {selectedCustomer && (
        <div className="customer-modal-overlay" onClick={() => setSelectedCustomer(null)}>
          <section className="customer-modal" onClick={(event) => event.stopPropagation()}>
            <button
              className="modal-close"
              type="button"
              onClick={() => setSelectedCustomer(null)}
              aria-label="Close"
            >
              ×
            </button>
            <div className="customer-modal-heading">
              <div className="customer-modal-avatar">
                {selectedCustomer.name?.charAt(0)?.toUpperCase() || "C"}
              </div>
              <div>
                <h2>{selectedCustomer.name}</h2>
                <p>{selectedCustomer.customer_id}</p>
              </div>
            </div>
            <div className="customer-details-grid">
              <div><span>Email</span><strong>{selectedCustomer.email}</strong></div>
              <div><span>City</span><strong>{selectedCustomer.city}</strong></div>
              <div><span>Segment</span><strong>{selectedCustomer.segment}</strong></div>
              <div><span>Last Order</span><strong>{selectedCustomer.last_order_date || "No delivered orders"}</strong></div>
              <div><span>Recency Score</span><strong>{selectedCustomer.recency_score}/5</strong></div>
              <div><span>Frequency Score</span><strong>{selectedCustomer.frequency_score}/5</strong></div>
              <div><span>Monetary Score</span><strong>{selectedCustomer.monetary_score}/5</strong></div>
              <div><span>Total RFM Score</span><strong>{selectedCustomer.rfm_score}/15</strong></div>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}


function DatasetsPage() {
  const [datasets, setDatasets] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [validation, setValidation] = useState(null);
  const [validationLoadingId, setValidationLoadingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadDatasets() {
    try {
      setLoading(true);
      setError("");
      const data = await getDatasets();
      setDatasets(Array.isArray(data) ? data : data.datasets || []);
    } catch (err) {
      console.error("Dataset loading error:", err);
      setError(err.response?.data?.detail || "Unable to load datasets. Check the backend.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDatasets();
  }, []);

  async function handleUpload() {
    if (!selectedFile) {
      setError("Please select a CSV file.");
      return;
    }
    try {
      setUploading(true);
      setError("");
      setSuccess("");
      await uploadDataset(selectedFile);
      setSelectedFile(null);
      const input = document.getElementById("dataset-file-input");
      if (input) input.value = "";
      setSuccess("Dataset uploaded successfully.");
      await loadDatasets();
    } catch (err) {
      setError(err.response?.data?.detail || "Dataset upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handlePreview(datasetId) {
    try {
      setPreviewLoading(true);
      setError("");
      const data = await previewDataset(datasetId, 10);
      setPreview(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to preview dataset.");
    } finally {
      setPreviewLoading(false);
    }
  }

  async function handleValidate(datasetId) {
    try {
      setValidationLoadingId(datasetId);
      setError("");
      setSuccess("");
      const data = await validateDataset(datasetId);
      setValidation(data);
    } catch (err) {
      console.error("Dataset validation error:", err);
      setError(err.response?.data?.detail || "Unable to validate dataset.");
    } finally {
      setValidationLoadingId(null);
    }
  }

  async function handleDelete(datasetId) {
    if (!window.confirm("Are you sure you want to delete this dataset?")) return;
    try {
      setError("");
      setSuccess("");
      await deleteDataset(datasetId);
      setSuccess("Dataset deleted successfully.");
      await loadDatasets();
      if (preview?.dataset_id === datasetId) setPreview(null);
      if (validation?.dataset_id === datasetId) setValidation(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to delete dataset.");
    }
  }

  function formatFileSize(bytes) {
    if (!bytes) return "0 KB";
    return bytes >= 1024 * 1024
      ? `${(bytes / (1024 * 1024)).toFixed(2)} MB`
      : `${(bytes / 1024).toFixed(2)} KB`;
  }

  function getIssueSummary(value) {
    if (!value || typeof value !== "object") return "0";
    const entries = Object.entries(value).filter(([, count]) => Number(count) > 0);
    return entries.length
      ? entries.map(([column, count]) => `${column}: ${count}`).join(", ")
      : "None";
  }

  const previewColumns = preview?.columns || [];
  const previewRows = preview?.preview || preview?.rows || preview?.data || [];

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>Datasets</h1>
            <p>Upload, manage and explore your customer datasets.</p>
          </div>
        </div>
      </header>

      {error && (
        <div className="dataset-alert dataset-error">
          <span>{error}</span>
          <button type="button" onClick={() => setError("")} aria-label="Dismiss"><X size={16} /></button>
        </div>
      )}
      {success && (
        <div className="dataset-alert dataset-success">
          <CheckCircle2 size={17} />
          <span>{success}</span>
          <button type="button" onClick={() => setSuccess("")} aria-label="Dismiss"><X size={16} /></button>
        </div>
      )}

      <section className="panel dataset-upload-panel">
        <div className="panel-header">
          <div>
            <h3>Upload Dataset</h3>
            <p>Select a CSV file to add it to your workspace.</p>
          </div>
          <FileSpreadsheet size={24} />
        </div>

        <label className="dataset-dropzone" htmlFor="dataset-file-input">
          <Upload size={30} />
          <strong>{selectedFile ? selectedFile.name : "Choose a CSV file"}</strong>
          <span>CSV files only · Maximum size 20 MB</span>
          <input
            id="dataset-file-input"
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => {
              const file = event.target.files?.[0];
              setError("");
              setSuccess("");
              if (file && !file.name.toLowerCase().endsWith(".csv")) {
                setSelectedFile(null);
                setError("Only CSV files are supported.");
                event.target.value = "";
                return;
              }
              if (file && file.size > 20 * 1024 * 1024) {
                setSelectedFile(null);
                setError("File size must be 20 MB or less.");
                event.target.value = "";
                return;
              }
              setSelectedFile(file || null);
            }}
          />
        </label>

        <div className="dataset-upload-actions">
          <span>{selectedFile ? formatFileSize(selectedFile.size) : "No file selected"}</span>
          <button type="button" onClick={handleUpload} disabled={!selectedFile || uploading}>
            <Upload size={16} />
            {uploading ? "Uploading..." : "Upload Dataset"}
          </button>
        </div>
      </section>

      <section className="panel datasets-list-panel">
        <div className="panel-header">
          <div>
            <h3>Uploaded Datasets</h3>
            <p>{datasets.length} datasets available</p>
          </div>
          <button type="button" className="dataset-refresh" onClick={loadDatasets} disabled={loading}>
            <RefreshCw size={16} /> Refresh
          </button>
        </div>

        {loading ? (
          <div className="customers-message"><RefreshCw size={22} className="spin" /><span>Loading datasets...</span></div>
        ) : datasets.length === 0 ? (
          <div className="customers-message"><Database size={26} /><span>No datasets uploaded yet.</span></div>
        ) : (
          <div className="table-wrapper">
            <table className="customers-table">
              <thead>
                <tr><th>Dataset</th><th>Rows</th><th>Columns</th><th>File Size</th><th>Uploaded At</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {datasets.map((dataset) => (
                  <tr key={dataset.dataset_id}>
                    <td><div className="dataset-file-name"><FileSpreadsheet size={18} />{dataset.original_filename}</div></td>
                    <td>{dataset.row_count}</td>
                    <td>{dataset.column_count}</td>
                    <td>{formatFileSize(dataset.file_size)}</td>
                    <td>{dataset.uploaded_at ? new Date(dataset.uploaded_at).toLocaleString() : "—"}</td>
                    <td>
                      <div className="dataset-actions">
                        <button
                          type="button"
                          title="Validate dataset"
                          className="dataset-validate"
                          onClick={() => handleValidate(dataset.dataset_id)}
                          disabled={validationLoadingId === dataset.dataset_id}
                        >
                          {validationLoadingId === dataset.dataset_id
                            ? <RefreshCw size={17} className="spin" />
                            : <ClipboardCheck size={17} />}
                        </button>
                        <button type="button" title="Preview" onClick={() => handlePreview(dataset.dataset_id)} disabled={previewLoading}><Eye size={17} /></button>
                        <button type="button" title="Delete" className="dataset-delete" onClick={() => handleDelete(dataset.dataset_id)}><Trash2 size={17} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {previewLoading && <div className="customers-message"><RefreshCw size={20} className="spin" /><span>Loading preview...</span></div>}

      {preview && (
        <div className="customer-modal-overlay" onClick={() => setPreview(null)}>
          <section className="customer-modal dataset-preview-modal" onClick={(event) => event.stopPropagation()}>
            <button className="modal-close" type="button" onClick={() => setPreview(null)} aria-label="Close preview">×</button>
            <h2>Dataset Preview</h2>
            <p>{preview.original_filename || preview.filename || "CSV preview"}</p>
            <div className="table-wrapper dataset-preview-table">
              <table className="customers-table">
                <thead><tr>{previewColumns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
                <tbody>
                  {previewRows.map((row, index) => (
                    <tr key={index}>
                      {previewColumns.map((column) => <td key={column}>{typeof row === "object" ? (row[column] ?? "") : ""}</td>)}
                    </tr>
                  ))}
                  {previewRows.length === 0 && <tr><td colSpan={Math.max(previewColumns.length, 1)}>No preview rows available.</td></tr>}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}
      {validation && (
        <div className="customer-modal-overlay" onClick={() => setValidation(null)}>
          <section
            className="customer-modal dataset-validation-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <button
              className="modal-close"
              type="button"
              onClick={() => setValidation(null)}
              aria-label="Close validation results"
            >
              ×
            </button>

            <div className="dataset-validation-heading">
              <div>
                <h2>Dataset Quality Report</h2>
                <p>{validation.filename || validation.original_filename || "Uploaded dataset"}</p>
              </div>
              <span className={`dataset-quality-status ${(validation.status || "").toLowerCase().replace(/\\s+/g, "-")}`}>
                {validation.status || "Validated"}
              </span>
            </div>

            <div className="dataset-quality-score">
              <div>
                <span>Overall data quality score</span>
                <strong>{Number(validation.quality_score || 0).toFixed(1)}%</strong>
              </div>
              <div className="dataset-quality-track">
                <div
                  className="dataset-quality-fill"
                  style={{
                    width: `${Math.min(100, Math.max(0, Number(validation.quality_score || 0)))}%`,
                    background:
                      Number(validation.quality_score || 0) >= 90
                        ? "#16a34a"
                        : Number(validation.quality_score || 0) >= 70
                          ? "#d69e2e"
                          : "#dc4545",
                  }}
                />
              </div>
            </div>

            <div className="dataset-quality-grid">
              <div className="dataset-quality-card">
                <span>Total Rows</span>
                <strong>{Number(validation.total_rows || 0).toLocaleString("en-IN")}</strong>
              </div>
              <div className="dataset-quality-card">
                <span>Total Columns</span>
                <strong>{Number(validation.total_columns || 0).toLocaleString("en-IN")}</strong>
              </div>
              <div className="dataset-quality-card">
                <span>Missing Values</span>
                <strong>{Number(validation.missing_values?.total || 0).toLocaleString("en-IN")}</strong>
              </div>
              <div className="dataset-quality-card">
                <span>Duplicate Rows</span>
                <strong>{Number(validation.duplicate_rows || 0).toLocaleString("en-IN")}</strong>
              </div>
              <div className="dataset-quality-card">
                <span>Empty Rows</span>
                <strong>{Number(validation.empty_rows || 0).toLocaleString("en-IN")}</strong>
              </div>
              <div className="dataset-quality-card">
                <span>Invalid Emails</span>
                <strong>{Number(validation.invalid_emails || 0).toLocaleString("en-IN")}</strong>
              </div>
            </div>

            <div className="dataset-validation-details">
              <h3>Validation Details</h3>
              <div className="dataset-validation-row">
                <span>Missing values by column</span>
                <strong>{getIssueSummary(validation.missing_values?.by_column)}</strong>
              </div>
              <div className="dataset-validation-row">
                <span>Invalid numeric values</span>
                <strong>{getIssueSummary(validation.invalid_numeric_values)}</strong>
              </div>
              <div className="dataset-validation-row">
                <span>Invalid date values</span>
                <strong>{getIssueSummary(validation.invalid_date_values)}</strong>
              </div>
              <p className="dataset-validation-note">
                The quality score is calculated from missing and invalid cell values.
                Duplicate and empty rows are displayed separately in this report.
              </p>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}


function DataQualityPage() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadOverview() {
      try {
        setLoading(true);
        setError("");
        const data = await getDatasetQualityOverview();
        if (!cancelled) setOverview(data);
      } catch (err) {
        console.error("Dataset quality overview error:", err);
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
            "Unable to load data quality overview. Check the backend endpoint."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadOverview();
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  if (loading) {
    return (
      <main className="main-content">
        <div className="loading-state">
          <RefreshCw size={24} className="spin" />
          <h2>Loading data quality overview...</h2>
          <p>Validating uploaded datasets</p>
        </div>
      </main>
    );
  }

  const statusData = overview?.status_distribution || [];
  const qualityData = overview?.dataset_quality || [];
  const missingData = overview?.missing_values_by_dataset || [];
  const recentData = overview?.recent_validations || [];

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>Data Quality Overview</h1>
            <p>Monitor the quality and reliability of your uploaded datasets.</p>
          </div>
        </div>
        <div className="topbar-actions">
          <button
            type="button"
            className="dataset-refresh"
            onClick={() => setRefreshKey((value) => value + 1)}
            disabled={loading}
          >
            <RefreshCw size={16} /> Refresh
          </button>
        </div>
      </header>

      {error && (
        <div className="dataset-alert dataset-error">
          <AlertCircle size={17} />
          <span>{error}</span>
        </div>
      )}

      {!error && overview && (
        <>
          <section className="stats-grid">
            <StatCard
              title="Total Datasets"
              value={Number(overview.total_datasets || 0).toLocaleString("en-IN")}
              icon={Database}
            />
            <StatCard
              title="Average Quality"
              value={`${Number(overview.average_quality_score || 0).toFixed(1)}%`}
              icon={ClipboardCheck}
            />
            <StatCard
              title="Needs Attention"
              value={Number(overview.datasets_needing_attention || 0).toLocaleString("en-IN")}
              icon={AlertCircle}
            />
            <StatCard
              title="Total Data Issues"
              value={Number(overview.total_issues || 0).toLocaleString("en-IN")}
              icon={FileSpreadsheet}
            />
          </section>

          {Number(overview.unavailable_datasets || 0) > 0 && (
            <div className="dataset-alert dataset-error">
              {overview.unavailable_datasets} dataset(s) could not be validated. Check the unavailable list below.
            </div>
          )}

          <section className="analytics-grid data-quality-charts">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>Dataset Quality Scores</h3>
                  <p>Quality score for each uploaded dataset</p>
                </div>
              </div>
              {qualityData.length ? (
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={qualityData} margin={{ top: 10, right: 12, left: 0, bottom: 55 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis
                        dataKey="filename"
                        angle={-25}
                        textAnchor="end"
                        interval={0}
                        height={65}
                        tick={{ fontSize: 10 }}
                      />
                      <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
                      <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, "Quality"]} />
                      <Bar dataKey="quality_score" name="Quality score" fill="#5146e5" radius={[5, 5, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="customers-message">No validated datasets available yet.</div>
              )}
            </div>

            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>Quality Status Distribution</h3>
                  <p>Number of datasets by validation status</p>
                </div>
              </div>
              {statusData.some((item) => Number(item.value) > 0) ? (
                <div className="pie-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={3}>
                        {statusData.map((item) => (
                          <Cell
                            key={item.name}
                            fill={
                              item.name === "Good" ? "#16a34a" :
                              item.name === "Needs Improvement" ? "#d69e2e" : "#dc4545"
                            }
                          />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value, name) => [`${value} datasets`, name]} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="customers-message">No status information available.</div>
              )}
              <div className="segment-legend">
                {statusData.map((item) => (
                  <div className="legend-item" key={item.name}>
                    <span>{item.name}</span>
                    <strong>{Number(item.value || 0)}</strong>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="panel data-quality-missing-panel">
            <div className="panel-header">
              <div>
                <h3>Missing Values by Dataset</h3>
                <p>Datasets with the highest number of missing cells</p>
              </div>
            </div>
            {missingData.length ? (
              <div className="table-wrapper">
                <table className="customers-table">
                  <thead>
                    <tr><th>Dataset</th><th>Missing Values</th><th>Quality Score</th></tr>
                  </thead>
                  <tbody>
                    {missingData.map((item) => (
                      <tr key={item.dataset_id}>
                        <td>{item.filename}</td>
                        <td>{Number(item.missing_values || 0).toLocaleString("en-IN")}</td>
                        <td>
                          <span className={`dataset-quality-status ${
                            Number(item.quality_score) >= 90 ? "good" :
                            Number(item.quality_score) >= 70 ? "needs-improvement" : "poor"
                          }`}>
                            {Number(item.quality_score || 0).toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="customers-message">No missing-value data available.</div>
            )}
          </section>

          <section className="panel data-quality-recent-panel">
            <div className="panel-header">
              <div>
                <h3>Recent Validation Results</h3>
                <p>Latest dataset validation reports</p>
              </div>
            </div>
            {recentData.length ? (
              <div className="table-wrapper">
                <table className="customers-table">
                  <thead>
                    <tr><th>Dataset</th><th>Rows</th><th>Columns</th><th>Quality Score</th><th>Status</th></tr>
                  </thead>
                  <tbody>
                    {recentData.map((item) => (
                      <tr key={item.dataset_id}>
                        <td>{item.filename}</td>
                        <td>{Number(item.total_rows || 0).toLocaleString("en-IN")}</td>
                        <td>{Number(item.total_columns || 0).toLocaleString("en-IN")}</td>
                        <td>{Number(item.quality_score || 0).toFixed(1)}%</td>
                        <td>
                          <span className={`dataset-quality-status ${
                            item.status === "Good" ? "good" :
                            item.status === "Needs Improvement" ? "needs-improvement" : "poor"
                          }`}>
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="customers-message">No validation reports yet.</div>
            )}
          </section>

          {overview.unavailable?.length > 0 && (
            <section className="panel data-quality-recent-panel">
              <div className="panel-header">
                <div>
                  <h3>Unavailable Datasets</h3>
                  <p>These files could not be read during validation</p>
                </div>
              </div>
              <div className="table-wrapper">
                <table className="customers-table">
                  <thead><tr><th>Dataset</th><th>Reason</th></tr></thead>
                  <tbody>
                    {overview.unavailable.map((item) => (
                      <tr key={item.dataset_id}>
                        <td>{item.filename}</td>
                        <td>{item.detail}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </>
      )}
    </main>
  );
}




function PredictionsPage() {
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [riskFilter, setRiskFilter] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadPredictions() {
      try {
        setLoading(true);
        setError("");

        const [summaryData, customerData, metricsData] = await Promise.all([
          getChurnSummary(),
          getChurnCustomers("", 5000),
          getChurnModelInfo(),
        ]);

        if (!cancelled) {
          setSummary(summaryData);
          setCustomers(customerData.predictions || []);
          setMetrics(metricsData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
            "Unable to load churn predictions. Check the backend API."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadPredictions();
    return () => { cancelled = true; };
  }, [refreshKey]);

  const filteredCustomers = customers.filter((customer) => {
    const matchesRisk = !riskFilter || customer.risk_level === riskFilter;
    const matchesSearch = customer.customer_id
      .toLowerCase()
      .includes(search.trim().toLowerCase());
    return matchesRisk && matchesSearch;
  });

  const riskData = summary ? [
    { name: "High Risk", value: summary.high_risk_customers, color: "#dc4545" },
    { name: "Medium Risk", value: summary.medium_risk_customers, color: "#d69e2e" },
    { name: "Low Risk", value: summary.low_risk_customers, color: "#16a34a" },
  ] : [];

  if (loading) {
    return (
      <main className="main-content">
        <div className="loading-state">
          <RefreshCw size={24} className="spin" />
          <h2>Loading churn predictions...</h2>
          <p>Scoring customer behavior with the trained ML model</p>
        </div>
      </main>
    );
  }

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>Churn Predictions</h1>
            <p>Identify customers who may stop engaging with your business.</p>
          </div>
        </div>
        <div className="topbar-actions">
          <button
            className="icon-button"
            type="button"
            aria-label="Refresh churn predictions"
            onClick={() => setRefreshKey((value) => value + 1)}
          >
            <RefreshCw size={18} />
          </button>
          <div className="date-filter">ML-powered analysis</div>
        </div>
      </header>

      {error && (
        <div className="dataset-alert dataset-error">
          <AlertCircle size={17} /> {error}
        </div>
      )}

      {summary && (
        <>
          <section className="stats-grid">
            <StatCard
              title="Total Customers"
              value={Number(summary.total_customers).toLocaleString("en-IN")}
              icon={Users}
            />
            <StatCard
              title="Predicted Churn"
              value={Number(summary.predicted_churn_customers).toLocaleString("en-IN")}
              icon={UserPlus}
            />
            <StatCard
              title="High-Risk Customers"
              value={Number(summary.high_risk_customers).toLocaleString("en-IN")}
              icon={ShieldAlert}
            />
            <StatCard
              title="Predicted Churn Rate"
              value={`${Number(summary.predicted_churn_percentage).toFixed(1)}%`}
              icon={Activity}
            />
          </section>

          <section className="analytics-grid">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>Customer Risk Distribution</h3>
                  <p>Model probability bands across all customers</p>
                </div>
              </div>
              <div className="pie-container">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={58}
                      outerRadius={92}
                      paddingAngle={3}
                    >
                      {riskData.map((item) => (
                        <Cell key={item.name} fill={item.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [Number(value).toLocaleString("en-IN"), "Customers"]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="segment-legend">
                {riskData.map((item) => (
                  <div className="legend-item" key={item.name}>
                    <span>{item.name}</span>
                    <strong>{Number(item.value).toLocaleString("en-IN")}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>Model Performance</h3>
                  <p>{metrics?.best_model || metrics?.model || "Trained classification model"}</p>
                </div>
              </div>
              <div className="churn-metric-grid">
                {[
                  ["Accuracy", metrics?.accuracy],
                  ["Precision", metrics?.precision],
                  ["Recall", metrics?.recall],
                  ["F1 Score", metrics?.f1_score],
                  ["ROC-AUC", metrics?.roc_auc],
                ].map(([label, value]) => (
                  <div className="churn-metric" key={label}>
                    <span>{label}</span>
                    <strong>{value == null ? "—" : `${(Number(value) * 100).toFixed(1)}%`}</strong>
                  </div>
                ))}
              </div>
              <p className="recommendation-footnote">
                Metrics are from the held-out test set. Risk bands are dashboard thresholds, not calibrated business decisions.
              </p>
            </div>
          </section>

          <section className="panel recommendation-panel">
            <div className="panel-header">
              <div>
                <h3>Customer Churn Risk</h3>
                <p>Predictions generated from the latest customer behavior features.</p>
              </div>
            </div>

            <div className="recommendation-search churn-filter-bar">
              <label htmlFor="churn-search">Search customer ID</label>
              <input
                id="churn-search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="e.g. CUST00001"
              />
              <label htmlFor="churn-risk-filter">Risk level</label>
              <select
                id="churn-risk-filter"
                value={riskFilter}
                onChange={(event) => setRiskFilter(event.target.value)}
              >
                <option value="">All risk levels</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            {filteredCustomers.length ? (
              <div className="table-wrapper">
                <table className="customers-table">
                  <thead>
                    <tr>
                      <th>Customer ID</th>
                      <th>Prediction</th>
                      <th>Churn Probability</th>
                      <th>Risk Level</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCustomers.slice(0, 100).map((customer) => (
                      <tr key={customer.customer_id}>
                        <td><strong>{customer.customer_id}</strong></td>
                        <td>{customer.churn_status}</td>
                        <td>{Number(customer.churn_probability).toFixed(2)}%</td>
                        <td>
                          <span className={`dataset-quality-status ${
                            customer.risk_level === "High" ? "poor" :
                            customer.risk_level === "Medium" ? "needs-improvement" : "good"
                          }`}>
                            {customer.risk_level}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {filteredCustomers.length > 100 && (
                  <p className="recommendation-footnote">
                    Showing first 100 of {filteredCustomers.length.toLocaleString("en-IN")} matching customers.
                  </p>
                )}
              </div>
            ) : (
              <div className="customers-message">No customers match these filters.</div>
            )}
          </section>
        </>
      )}
    </main>
  );
}


function RecommendationsPage() {
  const [summary, setSummary] = useState(null);
  const [popular, setPopular] = useState([]);
  const [bundles, setBundles] = useState([]);
  const [customerId, setCustomerId] = useState("CUST00001");
  const [customerResult, setCustomerResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [customerLoading, setCustomerLoading] = useState(false);
  const [error, setError] = useState("");
  const [customerError, setCustomerError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        setError("");
        const [summaryData, popularData, bundleData] = await Promise.all([
          getRecommendationSummary(),
          getPopularProducts(10),
          getFrequentlyBoughtTogether(10),
        ]);
        if (!cancelled) {
          setSummary(summaryData);
          setPopular(popularData);
          setBundles(bundleData);
        }
      } catch (err) {
        if (!cancelled) setError(err.response?.data?.detail || "Unable to load recommendation data. Check the backend API and database.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  async function findCustomerRecommendations(event) {
    event.preventDefault();
    if (!customerId.trim()) return;
    try {
      setCustomerLoading(true);
      setCustomerError("");
      const result = await getCustomerRecommendations(customerId.trim(), 10);
      setCustomerResult(result);
    } catch (err) {
      setCustomerResult(null);
      setCustomerError(err.response?.data?.detail || "Could not generate recommendations for this customer.");
    } finally {
      setCustomerLoading(false);
    }
  }

  if (loading) return (
    <main className="main-content"><div className="loading-state"><RefreshCw size={24} className="spin" /><h2>Loading recommendations...</h2><p>Analyzing delivered purchase history</p></div></main>
  );

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading"><div><h1>Recommendations</h1><p>Product suggestions based on actual purchase patterns.</p></div></div>
      </header>

      <div className="recommendation-method"><CheckCircle2 size={17} /> Rule-based recommendations · SQL + purchase history · No AI/ML model used</div>
      {error && <div className="dataset-alert dataset-error"><AlertCircle size={17} />{error}</div>}

      {summary && <section className="stats-grid">
        <StatCard title="Products in Catalog" value={Number(summary.total_products || 0).toLocaleString("en-IN")} icon={Package} />
        <StatCard title="Orders with Products" value={Number(summary.orders_with_products || 0).toLocaleString("en-IN")} icon={ShoppingCart} />
        <StatCard title="Units Sold" value={Number(summary.units_sold || 0).toLocaleString("en-IN")} icon={ShoppingBasket} />
        <StatCard title="Popular Products" value={popular.length.toLocaleString("en-IN")} icon={ShoppingBag} />
      </section>}

      <section className="panel recommendation-panel">
        <div className="panel-header"><div><h3>Personalized Customer Recommendations</h3><p>Find popular products in categories the customer has purchased before, excluding products already purchased.</p></div></div>
        <form className="recommendation-search" onSubmit={findCustomerRecommendations}>
          <label htmlFor="recommendation-customer-id">Customer ID</label>
          <input id="recommendation-customer-id" value={customerId} onChange={(event) => setCustomerId(event.target.value)} placeholder="e.g. CUST00001" />
          <button type="submit" disabled={customerLoading}><UserRoundSearch size={16} />{customerLoading ? "Finding..." : "Get Recommendations"}</button>
        </form>
        {customerError && <div className="dataset-alert dataset-error">{customerError}</div>}
        {customerResult && <>
          <p className="recommendation-customer-name">Recommendations for <strong>{customerResult.customer.name}</strong> ({customerResult.customer.customer_id})</p>
          {customerResult.recommendations.length ? <div className="recommendation-product-grid">
            {customerResult.recommendations.map((item) => <article className="recommendation-product" key={item.product_id}>
              <div className="recommendation-product-icon"><Package size={23} /></div>
              <div><h4>{item.product_name}</h4><p>{item.category || "Uncategorized"}</p><span>{Number(item.units_sold).toLocaleString("en-IN")} units sold</span></div>
            </article>)}
          </div> : <p className="recommendation-empty">No matching products found for this customer's purchase categories.</p>}
          <p className="recommendation-footnote">{customerResult.method}</p>
        </>}
      </section>

      <section className="panel recommendation-panel">
        <div className="panel-header"><div><h3>Popular Products</h3><p>Ranked by units sold across delivered orders.</p></div></div>
        {popular.length ? <div className="table-wrapper"><table className="customers-table"><thead><tr><th>Product</th><th>Category</th><th>Brand</th><th>Orders</th><th>Units Sold</th><th>Revenue</th></tr></thead><tbody>
          {popular.map((item) => <tr key={item.product_id}><td><strong>{item.product_name}</strong><div className="customer-id">{item.product_id}</div></td><td>{item.category || "—"}</td><td>{item.brand || "—"}</td><td>{Number(item.order_count).toLocaleString("en-IN")}</td><td>{Number(item.units_sold).toLocaleString("en-IN")}</td><td>{formatCurrency(item.revenue)}</td></tr>)}
        </tbody></table></div> : <p className="recommendation-empty">No product sales data found.</p>}
      </section>

      <section className="panel recommendation-panel">
        <div className="panel-header"><div><h3>Frequently Bought Together</h3><p>Product pairs appearing in the same delivered order.</p></div></div>
        {bundles.length ? <div className="table-wrapper"><table className="customers-table"><thead><tr><th>Product 1</th><th>Product 2</th><th>Orders Together</th></tr></thead><tbody>
          {bundles.map((item) => <tr key={`${item.product_id_1}-${item.product_id_2}`}><td>{item.product_name_1}</td><td>{item.product_name_2}</td><td><strong>{Number(item.together_count).toLocaleString("en-IN")}</strong></td></tr>)}
        </tbody></table></div> : <p className="recommendation-empty">No product pairs found in the same order.</p>}
      </section>
    </main>
  );
}


function SentimentAnalysisPage() {
  const [summary, setSummary] = useState(null);
  const [distribution, setDistribution] = useState([]);
  const [trends, setTrends] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [totalReviews, setTotalReviews] = useState(0);
  const [search, setSearch] = useState("");
  const [sentimentFilter, setSentimentFilter] = useState("");
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);
  const pageSize = 10;

  useEffect(() => {
    let cancelled = false;

    async function loadSentiment() {
      try {
        setLoading(true);
        setError("");

        const [summaryData, distributionData, trendsData, reviewsData] =
          await Promise.all([
            getSentimentSummary(),
            getSentimentDistribution(),
            getSentimentTrends(),
            getSentimentReviews({
              search,
              sentiment: sentimentFilter,
              limit: pageSize,
              offset,
            }),
          ]);

        if (!cancelled) {
          setSummary(summaryData);
          setDistribution(distributionData.distribution || []);
          setTrends(trendsData.trends || []);
          setReviews(reviewsData.reviews || []);
          setTotalReviews(reviewsData.total || 0);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
            "Unable to load sentiment analysis. Check the backend API."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadSentiment();
    return () => { cancelled = true; };
  }, [search, sentimentFilter, offset, refreshKey]);

  const sentimentColors = {
    Positive: "#16a34a",
    Negative: "#dc4545",
    Neutral: "#94a3b8",
  };

  const sentimentBadgeStyle = (sentiment) => ({
    display: "inline-flex",
    alignItems: "center",
    padding: "5px 10px",
    borderRadius: "999px",
    fontSize: "12px",
    fontWeight: 600,
    color: sentimentColors[sentiment] || "#475569",
    background:
      sentiment === "Positive" ? "#dcfce7" :
      sentiment === "Negative" ? "#fee2e2" : "#f1f5f9",
  });

  if (loading && !summary) {
    return (
      <main className="main-content">
        <div className="loading-state">
          <RefreshCw size={24} className="spin" />
          <h2>Loading sentiment analysis...</h2>
          <p>Analyzing customer reviews with VADER</p>
        </div>
      </main>
    );
  }

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>Sentiment Analysis</h1>
            <p>Understand customer opinions from review text and ratings.</p>
          </div>
        </div>
        <div className="topbar-actions">
          <button
            className="icon-button"
            type="button"
            aria-label="Refresh sentiment analysis"
            onClick={() => setRefreshKey((value) => value + 1)}
          >
            <RefreshCw size={18} />
          </button>
          <div className="date-filter">VADER text analysis</div>
        </div>
      </header>

      {error && (
        <div className="dataset-alert dataset-error">
          <AlertCircle size={17} /> {error}
        </div>
      )}

      {summary && (
        <>
          <section className="stats-grid">
            <StatCard
              title="Total Reviews"
              value={Number(summary.total_reviews || 0).toLocaleString("en-IN")}
              icon={MessageSquareText}
            />
            <StatCard
              title="Positive Reviews"
              value={`${Number(summary.positive_reviews || 0).toLocaleString("en-IN")} (${Number(summary.positive_percentage || 0).toFixed(1)}%)`}
              icon={CheckCircle2}
            />
            <StatCard
              title="Negative Reviews"
              value={`${Number(summary.negative_reviews || 0).toLocaleString("en-IN")} (${Number(summary.negative_percentage || 0).toFixed(1)}%)`}
              icon={AlertCircle}
            />
            <StatCard
              title="Average Rating"
              value={`${Number(summary.average_rating || 0).toFixed(2)} / 5`}
              icon={Target}
            />
          </section>

          <section className="analytics-grid">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>Sentiment Distribution</h3>
                  <p>Classification based on customer review text</p>
                </div>
              </div>
              <div className="pie-container">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={distribution}
                      dataKey="count"
                      nameKey="sentiment"
                      innerRadius={58}
                      outerRadius={92}
                      paddingAngle={3}
                    >
                      {distribution.map((item) => (
                        <Cell
                          key={item.sentiment}
                          fill={sentimentColors[item.sentiment] || "#94a3b8"}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value) => [
                        Number(value).toLocaleString("en-IN"),
                        "Reviews",
                      ]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="segment-legend">
                {distribution.map((item) => (
                  <div className="legend-item" key={item.sentiment}>
                    <span>
                      <span
                        style={{
                          display: "inline-block",
                          width: 9,
                          height: 9,
                          borderRadius: "50%",
                          marginRight: 8,
                          background: sentimentColors[item.sentiment],
                        }}
                      />
                      {item.sentiment} ({Number(item.percentage).toFixed(1)}%)
                    </span>
                    <strong>{Number(item.count).toLocaleString("en-IN")}</strong>
                  </div>
                ))}
              </div>
            </div>

            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>Monthly Sentiment Trends</h3>
                  <p>Number of reviews classified each month</p>
                </div>
              </div>
              <div style={{ width: "100%", height: 300, padding: "12px 8px 4px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="positive"
                      name="Positive"
                      stackId="1"
                      stroke="#16a34a"
                      fill="#16a34a"
                      fillOpacity={0.18}
                    />
                    <Area
                      type="monotone"
                      dataKey="neutral"
                      name="Neutral"
                      stackId="1"
                      stroke="#94a3b8"
                      fill="#94a3b8"
                      fillOpacity={0.18}
                    />
                    <Area
                      type="monotone"
                      dataKey="negative"
                      name="Negative"
                      stackId="1"
                      stroke="#dc4545"
                      fill="#dc4545"
                      fillOpacity={0.18}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>

          <section className="panel recommendation-panel">
            <div className="panel-header">
              <div>
                <h3>Customer Reviews</h3>
                <p>Search reviews and compare text sentiment with star ratings.</p>
              </div>
              <div className="date-filter">
                Rating agreement: {Number(summary.rating_sentiment_agreement || 0).toFixed(1)}%
              </div>
            </div>

            <div className="recommendation-search churn-filter-bar">
              <label htmlFor="sentiment-search">Search reviews</label>
              <input
                id="sentiment-search"
                value={search}
                onChange={(event) => {
                  setSearch(event.target.value);
                  setOffset(0);
                }}
                placeholder="Review ID, customer ID or text"
              />
              <label htmlFor="sentiment-filter">Sentiment</label>
              <select
                id="sentiment-filter"
                value={sentimentFilter}
                onChange={(event) => {
                  setSentimentFilter(event.target.value);
                  setOffset(0);
                }}
              >
                <option value="">All sentiments</option>
                <option value="Positive">Positive</option>
                <option value="Negative">Negative</option>
                <option value="Neutral">Neutral</option>
              </select>
            </div>

            {reviews.length ? (
              <>
                <div className="table-wrapper">
                  <table className="customers-table">
                    <thead>
                      <tr>
                        <th>Review</th>
                        <th>Customer</th>
                        <th>Rating</th>
                        <th>Review Sentiment</th>
                        <th>Rating Sentiment</th>
                        <th>Agreement</th>
                        <th>Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reviews.map((review) => (
                        <tr key={review.review_id}>
                          <td>
                            <strong>{review.review_text || "—"}</strong>
                            <div className="customer-id">{review.review_id}</div>
                          </td>
                          <td>{review.customer_id}</td>
                          <td>{review.rating == null ? "—" : `${review.rating} / 5`}</td>
                          <td>
                            <span style={sentimentBadgeStyle(review.sentiment)}>
                              {review.sentiment}
                            </span>
                          </td>
                          <td>{review.rating_sentiment || "—"}</td>
                          <td>
                            {review.sentiment_agreement == null
                              ? "—"
                              : review.sentiment_agreement
                                ? <span style={{ color: "#16a34a", fontWeight: 600 }}>Match</span>
                                : <span style={{ color: "#dc4545", fontWeight: 600 }}>Mismatch</span>}
                          </td>
                          <td>{review.review_date || "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: 12,
                    padding: "16px 0 4px",
                    flexWrap: "wrap",
                  }}
                >
                  <span className="recommendation-footnote">
                    Showing {offset + 1}–{Math.min(offset + pageSize, totalReviews)} of {totalReviews.toLocaleString("en-IN")} reviews
                  </span>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button
                      className="secondary-button"
                      type="button"
                      disabled={offset === 0 || loading}
                      onClick={() => setOffset((value) => Math.max(0, value - pageSize))}
                    >
                      Previous
                    </button>
                    <button
                      className="secondary-button"
                      type="button"
                      disabled={offset + pageSize >= totalReviews || loading}
                      onClick={() => setOffset((value) => value + pageSize)}
                    >
                      Next
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <p className="recommendation-empty">No reviews match your search or filter.</p>
            )}
          </section>

          <p className="recommendation-footnote" style={{ marginTop: 12 }}>
            Sentiment labels are generated from review text using VADER. Rating sentiment is derived separately from star ratings (4–5 positive, 3 neutral, 1–2 negative). These are rule-based classifications, not human-verified labels.
          </p>
        </>
      )}
    </main>
  );
}


// ==========================================
// SETTINGS PAGE
// ==========================================

const SETTINGS_STORAGE_KEY = "marketiq_settings";

const DEFAULT_SETTINGS = {
  profile: {
    name: "Admin User",
    email: "admin@marketiq.com",
    role: "Administrator",
  },
  appearance: {
    theme: "light",
  },
  notifications: {
    dashboardAlerts: true,
    churnAlerts: true,
    dataQualityAlerts: true,
    systemNotifications: false,
  },
};

function getSavedSettings() {
  try {
    const saved = localStorage.getItem(SETTINGS_STORAGE_KEY);

    if (!saved) return DEFAULT_SETTINGS;

    const parsed = JSON.parse(saved);

    return {
      ...DEFAULT_SETTINGS,
      ...parsed,
      profile: {
        ...DEFAULT_SETTINGS.profile,
        ...parsed.profile,
      },
      appearance: {
        ...DEFAULT_SETTINGS.appearance,
        ...parsed.appearance,
      },
      notifications: {
        ...DEFAULT_SETTINGS.notifications,
        ...parsed.notifications,
      },
    };
  } catch (error) {
    console.error("Unable to read saved settings:", error);
    return DEFAULT_SETTINGS;
  }
}

function SettingsPage() {
  const [settings, setSettings] = useState(getSavedSettings);
  const [savedMessage, setSavedMessage] = useState("");

  // Apply theme immediately when changed
  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      settings.appearance.theme
    );
  }, [settings.appearance.theme]);

  function updateProfile(field, value) {
    setSettings((previous) => ({
      ...previous,
      profile: {
        ...previous.profile,
        [field]: value,
      },
    }));

    setSavedMessage("");
  }

  function updateNotification(field, value) {
    setSettings((previous) => ({
      ...previous,
      notifications: {
        ...previous.notifications,
        [field]: value,
      },
    }));

    setSavedMessage("");
  }

  function updateTheme(theme) {
    setSettings((previous) => ({
      ...previous,
      appearance: {
        ...previous.appearance,
        theme,
      },
    }));

    setSavedMessage("");
  }

  function saveSettings(event) {
    event.preventDefault();

    try {
      localStorage.setItem(
        SETTINGS_STORAGE_KEY,
        JSON.stringify(settings)
      );

      setSavedMessage("Your settings have been saved successfully.");
    } catch (error) {
      console.error("Unable to save settings:", error);
      setSavedMessage("Unable to save settings. Check browser storage.");
    }
  }

  function resetSettings() {
    const confirmed = window.confirm(
      "Are you sure you want to restore the default settings?"
    );

    if (!confirmed) return;

    setSettings(DEFAULT_SETTINGS);

    localStorage.setItem(
      SETTINGS_STORAGE_KEY,
      JSON.stringify(DEFAULT_SETTINGS)
    );

    setSavedMessage("Settings restored to defaults.");
  }

  return (
    <main className="main-content settings-page">

      {/* HEADER */}

      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>Settings</h1>
            <p>
              Manage your account, preferences and application settings.
            </p>
          </div>
        </div>
      </header>

      <form onSubmit={saveSettings}>

        {/* PROFILE SETTINGS */}

        <section className="panel settings-panel">

          <div className="settings-section-heading">
            <div className="settings-icon">
              <UserRound size={20} />
            </div>

            <div>
              <h3>Profile Settings</h3>
              <p>Manage your administrator profile information.</p>
            </div>
          </div>

          <div className="settings-form-grid">

            <div className="settings-field">
              <label htmlFor="profile-name">Full Name</label>

              <input
                id="profile-name"
                type="text"
                value={settings.profile.name}
                onChange={(event) =>
                  updateProfile("name", event.target.value)
                }
                placeholder="Enter your name"
              />
            </div>

            <div className="settings-field">
              <label htmlFor="profile-email">Email Address</label>

              <input
                id="profile-email"
                type="email"
                value={settings.profile.email}
                onChange={(event) =>
                  updateProfile("email", event.target.value)
                }
                placeholder="Enter your email"
              />
            </div>

            <div className="settings-field">
              <label htmlFor="profile-role">Role</label>

              <input
                id="profile-role"
                type="text"
                value={settings.profile.role}
                onChange={(event) =>
                  updateProfile("role", event.target.value)
                }
                placeholder="Enter your role"
              />
            </div>

          </div>
        </section>

        {/* APPEARANCE SETTINGS */}

        <section className="panel settings-panel">

          <div className="settings-section-heading">
            <div className="settings-icon">
              <Palette size={20} />
            </div>

            <div>
              <h3>Appearance</h3>
              <p>Customize the appearance of your workspace.</p>
            </div>
          </div>

          <div className="settings-theme-options">

            <button
              type="button"
              className={`theme-option ${
                settings.appearance.theme === "light"
                  ? "selected"
                  : ""
              }`}
              onClick={() => updateTheme("light")}
            >
              <div className="theme-preview light-preview">
                <Sun size={27} />
                <div className="theme-preview-lines">
                  <span />
                  <span />
                  <span />
                </div>
              </div>

              <div className="theme-option-label">
                <strong>Light Mode</strong>
                <span>Clean and bright interface</span>
              </div>

              {settings.appearance.theme === "light" && (
                <CheckCircle2 size={19} className="theme-check" />
              )}
            </button>

            <button
              type="button"
              className={`theme-option ${
                settings.appearance.theme === "dark"
                  ? "selected"
                  : ""
              }`}
              onClick={() => updateTheme("dark")}
            >
              <div className="theme-preview dark-preview">
                <Moon size={27} />
                <div className="theme-preview-lines">
                  <span />
                  <span />
                  <span />
                </div>
              </div>

              <div className="theme-option-label">
                <strong>Dark Mode</strong>
                <span>Comfortable low-light interface</span>
              </div>

              {settings.appearance.theme === "dark" && (
                <CheckCircle2 size={19} className="theme-check" />
              )}
            </button>

          </div>
        </section>

        {/* NOTIFICATION SETTINGS */}

        <section className="panel settings-panel">

          <div className="settings-section-heading">
            <div className="settings-icon">
              <Bell size={20} />
            </div>

            <div>
              <h3>Notifications</h3>
              <p>Choose which application alerts you want enabled.</p>
            </div>
          </div>

          <div className="settings-toggle-list">

            {[
              {
                key: "dashboardAlerts",
                title: "Dashboard Alerts",
                description: "General business dashboard alerts.",
              },
              {
                key: "churnAlerts",
                title: "Churn Risk Alerts",
                description: "Alerts related to high-risk customers.",
              },
              {
                key: "dataQualityAlerts",
                title: "Data Quality Alerts",
                description: "Notifications about dataset quality issues.",
              },
              {
                key: "systemNotifications",
                title: "System Notifications",
                description: "Application and system-related notifications.",
              },
            ].map((item) => (
              <div className="settings-toggle-row" key={item.key}>
                <div className="settings-toggle-info">
                  <strong>{item.title}</strong>
                  <span>{item.description}</span>
                </div>

                <label className="settings-switch">
                  <input
                    type="checkbox"
                    checked={settings.notifications[item.key]}
                    onChange={(event) =>
                      updateNotification(
                        item.key,
                        event.target.checked
                      )
                    }
                  />

                  <span className="settings-slider" />
                </label>
              </div>
            ))}

          </div>
        </section>
        {/* ABOUT */}

        <section className="panel settings-panel">

          <div className="settings-section-heading">
            <div className="settings-icon">
              <Info size={20} />
            </div>

            <div>
              <h3>About MarketIQ</h3>
              <p>Application information and version details.</p>
            </div>
          </div>

          <div className="settings-about">
            <div className="settings-about-logo">MI</div>

            <div>
              <h3>MarketIQ</h3>
              <p>Customer Behavior & Marketing Intelligence</p>
              <span>Version 1.0.0 · Development Build</span>
            </div>
          </div>

        </section>

        {/* ACTIONS */}

        <div className="settings-actions">

          <div className="settings-save-message">
            {savedMessage && (
              <span>
                <CheckCircle2 size={16} />
                {savedMessage}
              </span>
            )}
          </div>

          <div className="settings-action-buttons">

            <button
              type="button"
              className="settings-reset-button"
              onClick={resetSettings}
            >
              <RotateCcw size={16} />
              Reset Defaults
            </button>

            <button
              type="submit"
              className="settings-save-button"
            >
              <Save size={17} />
              Save Changes
            </button>

          </div>

        </div>

      </form>

    </main>
  );
}

function ComingSoon({ page }) {
  const item = navigation.find((nav) => nav.name === page);
  const Icon = item?.icon || Settings;

  const descriptions = {
    "AI Assistant":
      "Get intelligent insights about customer behavior and marketing performance.",
    Settings:
      "Manage your MarketIQ preferences and application settings.",
  };

  const features = {
    "AI Assistant": [
      "Ask questions about customer data",
      "Generate customer behavior insights",
      "Create personalized marketing strategies",
      "Get AI-powered business recommendations",
    ],
    Settings: [
      "Manage your profile",
      "Customize application appearance",
      "Configure notification preferences",
      "Manage application settings",
    ],
  };

  return (
    <main className="main-content">
      <header className="topbar">
        <div className="page-heading">
          <div>
            <h1>{page}</h1>
            <p>Customer Behavior & Marketing Intelligence</p>
          </div>
        </div>
      </header>

      <section
        className="panel"
        style={{
          padding: "60px 30px",
          textAlign: "center",
          minHeight: "450px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: "85px",
            height: "85px",
            borderRadius: "22px",
            background: "#eeedff",
            color: "#5146e5",
            display: "grid",
            placeItems: "center",
            marginBottom: "24px",
          }}
        >
          <Icon size={42} />
        </div>

        <span
          style={{
            background: "#eeedff",
            color: "#5146e5",
            padding: "7px 14px",
            borderRadius: "20px",
            fontSize: "11px",
            fontWeight: 700,
            marginBottom: "16px",
          }}
        >
          COMING SOON
        </span>

        <h2 style={{ fontSize: "25px", margin: "0 0 12px" }}>
          {page} is under development
        </h2>

        <p
          style={{
            color: "#9298a8",
            fontSize: "13px",
            maxWidth: "480px",
            lineHeight: 1.7,
            margin: "0 0 25px",
          }}
        >
          {descriptions[page] ||
            "This module is currently under development and will be available in a future update."}
        </p>

        {features[page] && (
          <div
            style={{
              textAlign: "left",
              marginBottom: "28px",
              width: "100%",
              maxWidth: "380px",
            }}
          >
            {features[page].map((feature, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  padding: "9px 0",
                  fontSize: "12px",
                  color: "#555b6c",
                }}
              >
                <CheckCircle2 size={16} color="#5146e5" />
                {feature}
              </div>
            ))}
          </div>
        )}

        <button
          type="button"
          onClick={() => window.location.reload()}
          style={{
            background: "#5146e5",
            color: "#fff",
            border: 0,
            borderRadius: "8px",
            padding: "12px 22px",
            fontSize: "13px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Refresh Page
        </button>
      </section>
    </main>
  );
}



export default function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  // Restore the saved theme when the application starts
  useEffect(() => {
    try {
      const saved = localStorage.getItem("marketiq_settings");
      const settings = saved ? JSON.parse(saved) : null;
      const theme = settings?.appearance?.theme || "light";

      document.documentElement.setAttribute("data-theme", theme);
    } catch (error) {
      document.documentElement.setAttribute("data-theme", "light");
    }
  }, []);

  return (
    <div className="app-layout">

      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
      />

      {activePage === "Dashboard" ? (
        <Dashboard />
      ) : activePage === "Customers" ? (
        <CustomersPage />
      ) : activePage === "Segmentation" ? (
        <SegmentationPage />
      ) : activePage === "Datasets" ? (
        <DatasetsPage />
      ) : activePage === "Data Quality" ? (
        <DataQualityPage />
      ) : activePage === "Predictions" ? (
        <PredictionsPage />
      ) : activePage === "Recommendations" ? (
        <RecommendationsPage />
      ) : activePage === "Settings" ? (
        <SettingsPage />
      ) : (
        <ComingSoon page={activePage} />
      )}

    </div>
  );
}

